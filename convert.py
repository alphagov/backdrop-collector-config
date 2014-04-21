
import json
import re
import sys

from os import listdir, makedirs
from os.path import join, isfile, exists

# To generate the data set mapping json file run the following javascript:
#
# var rows = document.querySelectorAll('#result_list tr');
# JSON.stringify(Array.prototype.reduce.call(rows, function(datasets, row) {
#
#   var arr = Array.prototype.map.call(row.children, function(col) {
#     return col.innerText;
#   });
#
#   datasets[arr[0]] = { "data-group": arr[1], "data-type": arr[2] }
#
#   return datasets;
#
# }, {}), null, '  ');
#
# on the page: https://[stagecraft_url]/admin/datasets/dataset/?all=


def read_json(path):
    with open(path) as json_fd:
        return json.load(json_fd)


def is_pingdom(json):
    return json.get('check_name', None) is not None


def is_ga(json):
    return json.get('query', None) is not None


def is_ga_realtime(json):
    return is_ga(json) and json.get('collector', None) is not None


def is_ga_trending(json):
    return is_ga(json) and json['query'].get('metric', None) is not None


def is_ga_content(json):
    return is_ga(json) and json.get('filtersets', None) is not None


def convert(query_json, data_set_mapping):
    if is_pingdom(query_json):
        print 'It is a Pingdom query'
        new_query = {
            'entrypoint': 'backdrop.collector.pingdom',
            'data-set': data_set_mapping[query_json['bucket']],
            'query': {
                'name': query_json['check_name'],
            },
            'options': {}
        }
    elif is_ga_realtime(query_json):
        print 'It is a GA Realtime query'
        new_query = {
            'query': query_json['query'],
            'entrypoint': 'backdrop.collector.ga.realtime',
            'data-set': data_set_mapping[query_json['target']],
            'options': {},
        }
    elif is_ga(query_json):
        data_set_re = re.compile('^.+/([^/]+)$')
        data_set_match = re.match(data_set_re, query_json['target']['url'])

        if not data_set_match:
            raise Exception('Could not find a data_set for query')

        new_query = {
            'query': query_json['query'],
            'data-set': data_set_mapping[data_set_match.group(1)],
        }

        if is_ga_trending(query_json):
            print 'It is a GA Trending query'
            new_query['entrypoint'] = 'backdrop.collector.ga.trending'
        elif is_ga_content(query_json):
            print 'It is a GA Content query'
            new_query['entrypoint'] = \
                'backdrop.collector.ga.contrib.content.table'
        else:
            print 'It is a GA query'
            new_query['entrypoint'] = 'backdrop.collector.ga'

        new_query['options'] = \
            {k: query_json[k] for k in
                set(query_json.keys()) - set(['query', 'target', 'dataType'])}

    return new_query


def save(query):
    data_group_path = './queries/{0}'.format(query['data-set']['data-group'])
    path = '{0}/{1}.json'.format(data_group_path,
                                 query['data-set']['data-type'])

    if isfile(path):
        print 'Converted query already exists at {0}'.format(path)
    else:
        if not exists(data_group_path):
            makedirs(data_group_path)

        with open(path, 'w') as new_query_fd:
            json.dump(query, new_query_fd, sort_keys=True, indent=2)
            print 'Saved converted query to {0}'.format(path)


def main():
    if len(sys.argv) != 3:
        print 'Usage: python convert.py [data_set_mapping] [path_to_queries]'
        return

    data_set_mapping = read_json(sys.argv[1])

    queries_path = sys.argv[2]
    queries = [join(queries_path, f) for f in listdir(queries_path)
               if isfile(join(queries_path, f))]

    for query_path in queries:
        print 'Converting {0}'.format(query_path)
        query_json = read_json(query_path)
        new_query_json = convert(query_json, data_set_mapping)
        save(new_query_json)


if __name__ == '__main__':
    main()
