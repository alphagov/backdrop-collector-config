
import json
import os
import sys


def generate_sql_statement(query, env_config, token_path):
    with open(query) as query_fd:
        query_json = json.load(query_fd)
    with open(os.path.join(env_config, token_path)) as token_fd:
        token_json = json.load(token_fd)

    token = token_json['token']
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
            if len(parts) == 5:
                query = parts[1]
                token = parts[3]
                print generate_sql_statement(query, env_config, token)
    print 'COMMIT;'


if __name__ == '__main__':
    main()
