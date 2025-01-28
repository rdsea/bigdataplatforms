# CS-E4640
## Simple example for studying big data platforms
import argparse
from time import time

from cassandra import ConsistencyLevel
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

parser = argparse.ArgumentParser()
parser.add_argument("--hosts", help='cassandra host "host1,host2,host3"')
parser.add_argument("--u", help="user name")
parser.add_argument("--p", help="password")
parser.add_argument("--q", help="input query")

args = parser.parse_args()
hosts = args.hosts.split(",")
auth_provider = PlainTextAuthProvider(username=args.u, password=args.p)

if __name__ == "__main__":
    # you can add some fake ips into cluster: '10.166.0.14','192.168.1.1'
    cluster = Cluster(hosts, port=9042, auth_provider=auth_provider)
    session = cluster.connect()
    ## Change the consistency level to see
    input = args.q
    # copy a line of the bird song in csv file here
    start = time()
    ## enable only 1 option
    consistency_level = ConsistencyLevel.ONE
    # consistency_level =ConsistencyLevel.QUORUM
    # consistency_level =ConsistencyLevel.ALL
    query = SimpleStatement(input, consistency_level=consistency_level)
    rows = session.execute(query)
    for row in rows:
        print(row)
    stop = time()
    print("It took", stop - start, "(s)", sep=" ")
