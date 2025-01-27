"""
Simple example for studying queue-based data ingestion
"""

import argparse
import os
import time

from dotenv import load_dotenv
from redis import Redis
from rq import Queue
from task import ingest_csv_file

load_dotenv()

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--uri", help="the URI of the dataset")
    parser.add_argument("--queuename", help="a queue name")
    args = parser.parse_args()

    """
    Get redis connection, you can use a free redis instance from redislab.
    You can also deploy your own redis instance.
    """
    redis = Redis(
        os.getenv("REDIS_HOST"),
        int(os.getenv("REDIS_PORT")),
        password=os.getenv("REDIS_PASSWORD"),
    )
    # use_connection(redis)

    # Make a simple task queue.
    # You can try to design different names, priorities, etc.
    queue_name = args.queuename  # make a simple queue name
    q = Queue(queue_name, connection=redis)

    """
    Just call a single job
    You can try to study how to schedule the jobs, etc.
    If you call many jobs, you have to manage the queues and the way to receive the result
    """
    job = q.enqueue(ingest_csv_file, args.uri)

    # Simple loops to see the result

    while job.result is None:
        time.sleep(2)
        print(job.result)
