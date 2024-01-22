# CS-E4640
## Simple example for studying big data platforms
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider
from cassandra.query import SimpleStatement
from time import time
import argparse
if __name__ == "__main__":        
    parser = argparse.ArgumentParser()
    parser.add_argument('--hosts', help='cassandra host, "e.g., "host1,host2,host3"')
    parser.add_argument('--port', default=9042,help='cassandra port')
    parser.add_argument('--u',help='user name')
    parser.add_argument('--p',help='password')
    parser.add_argument('--q',help='query')
    args = parser.parse_args()
    hosts=args.hosts.split(',')
    port =int(args.port)
    auth_provider = PlainTextAuthProvider(
        username=args.u, password=args.p)

    cluster = Cluster(hosts,port=port,auth_provider=auth_provider)
    start=time()
    session = cluster.connect()
    input =args.q

    query = SimpleStatement(input)
    session.execute(query)
    stop=time()
    print("It took",stop-start,"(s)",sep=" ")
