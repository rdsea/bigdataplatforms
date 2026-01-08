# CS-E4640
# Simple example for studying big data platforms
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

args = parser.parse_args()
hosts = args.hosts.split(",")
auth_provider = PlainTextAuthProvider(username=args.u, password=args.p)

if __name__ == "__main__":
    # you can add some fake ips into cluster: '10.166.0.14','192.168.1.1'
    cluster = Cluster(hosts, port=9042, auth_provider=auth_provider)
    session = cluster.connect()
    # replace values with data from dataset
    # or change the code so that it reads data from the file
    # input 1
    '''
    input= """
    INSERT INTO tutorial3.bird1234 (TIMESTAMP,CITY,ZIP,EGRIDREGION,TEMPERATUREF,HUMIDITY,DATA_AVAILABILITY_WEATHER,WETBULBTEMPERATUREF,COAL,HYDRO,NATURALGAS,NUCLEAR)
    VALUES
    (2019-01-03 18:00:00,Austin,78704,ERCT,42,76,1,37.9783997397202,58235,2692,56099,19019)

    ;
    """
    '''
    # input 2
    input2 = """
    INSERT INTO tutorial3.water1234 (TIMESTAMP,CITY,ZIP,EGRIDREGION,TEMPERATUREF)
    VALUES
    (2019-01-19 03:00:00,Austin,78704,ERCT,65)
    ;
    """

    start = time()
    ## enable only 1 option
    # consistency_level =ConsistencyLevel.ONE
    # consistency_level =ConsistencyLevel.QUORUM
    consistency_level = ConsistencyLevel.ALL
    ## correct the input
    query = SimpleStatement(input2, consistency_level=consistency_level)
    session.execute(query)
    stop = time()
    print("It took", stop - start, "(s)", sep=" ")
