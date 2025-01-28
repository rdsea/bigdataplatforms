#!/usr/bin/python3
import argparse
import sys

from pymongo import MongoClient

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--service_url", default="mongodb://localhost:27017", help="URL of the server"
    )
    args = parser.parse_args()
    url = args.service_url
    if url:
        client = MongoClient(url)
        result = client.db_name.command("ping")
        if result is None:
            print("Problem")
            sys.exit(2)
