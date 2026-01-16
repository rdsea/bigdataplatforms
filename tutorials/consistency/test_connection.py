import argparse
from time import time
from cassandra.auth import PlainTextAuthProvider
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement

if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("--hosts", required=True, help='comma-separated host list, e.g. "34.88.246.130"')
    p.add_argument("--port", default=9042, type=int)
    p.add_argument("--u", required=True, help="username")
    p.add_argument("--p", required=True, help="password")
    p.add_argument("--q", default="SELECT release_version FROM system.local;")
    args = p.parse_args()

    auth = PlainTextAuthProvider(username=args.u, password=args.p)
    hosts = [h.strip() for h in args.hosts.split(",") if h.strip()]

    t0 = time()
    cluster = Cluster(contact_points=hosts, port=args.port, auth_provider=auth)
    session = cluster.connect()  # no keyspace needed for fully-qualified queries
    rows = session.execute(SimpleStatement(args.q))
    for r in rows:
        print(r)
    print("It took", round(time()-t0, 3), "s")
    cluster.shutdown()
