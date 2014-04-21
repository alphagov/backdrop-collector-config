
import json
import os


entrypoint_information = {
    'backdrop.collector.ga': {
        'credentials': 'credentials/ga.json',
        'repeat': 'daily',
    },
    'backdrop.collector.ga.trending': {
        'credentials': 'credentials/ga.json',
        'repeat': 'daily',
    },
    'backdrop.collector.ga.contrib.content.table': {
        'credentials': 'credentials/ga.json',
        'repeat': 'daily',
    },
    'backdrop.collector.ga.realtime': {
        'credentials': 'credentials/ga.json',
        'repeat': '2minute',
    },
    'backdrop.collector.pingdom': {
        'credentials': 'credentials/pingdom.json',
        'repeat': 'hourly',
    },
}


def daily(jobs):
    entries = ['#', '# Daily jobs', '#', '']
    for index, (query, credentials, token) in enumerate(jobs):
        hour, minute = divmod(index, 60)
        entries.append('{0} {1} * * *,{2},{3},{4},backdrop.json'.format(minute, hour, query, credentials, token))
    return entries


def hourly(jobs):
    entries = ['#', '# Hourly jobs', '#', '']
    for index, (query, credentials, token) in enumerate(jobs):
        minute = index % 60
        entries.append('{0} * * * *,{1},{2},{3},backdrop.json'.format(minute, query, credentials, token))
    return entries


def two_minute(jobs):
    entries = ['#', '# Run every two minutes', '#', '']
    for index, (query, credentials, token) in enumerate(jobs):
        entries.append('1-59/2 * * * *,{0},{1},{2},backdrop.json'.format(query, credentials, token))
    return entries


def main():
    queries = [os.path.join(dp, f) for dp, dn, filenames in os.walk('queries') for f in filenames if os.path.splitext(f)[1] == '.json']
    time_buckets = {}

    for query in queries:
        with open(query) as query_fd:
            query_json = json.load(query_fd)
            entrypoint = query_json['entrypoint']
            token_file = "tokens/{0}.json".format(query_json['token'])

        query_info = entrypoint_information.get(entrypoint, None)

        if query_info is None:
            print "No entrypoint {0} from {1}".format(entrypoint, query)
        else:
            if query_info['repeat'] not in time_buckets:
                time_buckets[query_info['repeat']] = []

            time_buckets[query_info['repeat']].append((query, query_info['credentials'], token_file))

    daily_jobs = daily(time_buckets['daily'])
    hourly_jobs = hourly(time_buckets['hourly'])
    two_minute_jobs = two_minute(time_buckets['2minute'])

    spacer = ['', '']
    cronjobs_content = [
        '#',
        '# This file was generated by cronjobs.py',
        '#',
    ] + spacer + daily_jobs + spacer + hourly_jobs + spacer + two_minute_jobs

    print '\n'.join(cronjobs_content)


if __name__ == '__main__':
    main()
