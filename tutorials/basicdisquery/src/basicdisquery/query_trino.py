"""
Used to query a single source of data
"""

import argparse
import sys

import trino
import yaml

EX_NAMES = ["mongodb", "cassandra", "bigquery"]
# pre-define queries
SAMPLE_QUERIES = {
    "mongodb": "SELECT * FROM test.listings LIMIT 10",
    "cassandra": "select * from tutorial12345.bird1234 LIMIT 10",
    "bigquery": "SELECT * FROM taxitesting.taxi_trips LIMIT 20",
}
if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--config_file", help="YAML config file")
    parser.add_argument(
        "--ex_name", help='name of the example in ["mongodb","cassandra","bigquery"]'
    )
    args = parser.parse_args()
    config_file = args.config_file
    ex_name = args.ex_name
    if ex_name not in EX_NAMES:
        print(f"Input example name: {ex_name} must be one of {EX_NAMES}")
        sys.exit(1)
    with open(config_file, encoding="utf-8") as config_fp:
        config = yaml.load(config_fp, Loader=yaml.BaseLoader)
    connection_conf = config[ex_name]
    trino_conn = trino.dbapi.connect(**connection_conf)
    # run the query and print the result
    cursor = trino_conn.cursor()
    cursor.execute(SAMPLE_QUERIES[ex_name])
    rows = cursor.fetchall()
    print(f'Results for "{SAMPLE_QUERIES[ex_name]}"')
    for row in rows:
        print(row)
