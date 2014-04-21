
import json
import os
import sys


def generate_sql_statement(query, env_config, service):
    with open(query) as query_fd:
        query_json = json.load(query_fd)
    with open(os.path.join(env_config, service)) as service_fd:
        service_json = json.load(service_fd)

    token = service_json['backdrop']['token']
    data_group = query_json['data-set']['data-group']
    data_type = query_json['data-set']['data-type']

    return 'UPDATE datasets_dataset SET bearer_token=\'{0}\' ' \
           'WHERE data_group_id=(SELECT id FROM datasets_datagroup WHERE name=\'{1}\') ' \
           'AND data_type_id=(SELECT id FROM datasets_datatype WHERE name=\'{2}\');'.format(token, data_group, data_type)


def main():
    if len(sys.argv) != 2:
        print 'Usage: python tools/update_token.py [environment_app_config]'
        return

    env_config = sys.argv[1]

    print 'BEGIN;'
    with open('./cronjobs') as cronjobs:
        for cronjob in cronjobs:
            parts = cronjob.strip().split(',')
            if len(parts) == 3:
                query = parts[1]
                service = parts[2]
                print generate_sql_statement(query, env_config, service)
    print 'COMMIT;'


if __name__ == '__main__':
    main()
