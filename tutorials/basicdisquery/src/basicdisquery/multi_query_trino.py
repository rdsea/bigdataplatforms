"""
Used to send a sql querying multiple data sources at the same time
"""
import argparse
import yaml
import trino

if __name__ == '__main__':
    parser = argparse.ArgumentParser()
    parser.add_argument('--config_file', help='YAML config with an entry name "common"')
    parser.add_argument('--sql_stmt',
                        help='sql file')
    args = parser.parse_args()
    config_file = args.config_file
    sql_stmt_file = args.sql_stmt
    with open(config_file, mode="r", encoding="utf-8") as config_fp:
        config = yaml.load(config_fp,Loader=yaml.BaseLoader)
    with open(sql_stmt_file, mode="r", encoding="utf-8") as stmt_fp:
        sql_stmt = stmt_fp.read()
    connection_conf = config["common"]
    trino_conn = trino.dbapi.connect(**connection_conf)
    # run the query and print the result
    cursor = trino_conn.cursor()
    cursor.execute(sql_stmt)
    rows = cursor.fetchall()
    print(f'Results for "{sql_stmt}"')
    for row in rows:
        print(row)
