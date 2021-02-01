# CS-E4640
#Simple example for studying big data platforms
from cassandra import ConsistencyLevel
from cassandra.cluster import Cluster
from cassandra.query import SimpleStatement
from cassandra.auth import PlainTextAuthProvider
from time import time
import argparse
parser = argparse.ArgumentParser()
parser.add_argument('--hosts', help='cassandra host "host1,host2,host3"')
parser.add_argument('--u',help='user name')
parser.add_argument('--p',help='password')

args = parser.parse_args()
hosts=args.hosts.split(',')
auth_provider = PlainTextAuthProvider(
        username=args.u, password=args.p)

if __name__ == "__main__":
    #you can add some fake ips into cluster: '10.166.0.14','192.168.1.1'
    cluster = Cluster(hosts,port=9042,auth_provider=auth_provider)
    session = cluster.connect()
    # replace values with data from dataset
    # or change the code so that it reads data from the file
    #input 1
    '''
    input= """
    INSERT INTO tutorial02149.bird1234 (country, duration_seconds, english_cname, id,  species, latitude, longitude)
    VALUES
    ('Mexico',29,'Black-tailed Gnatcatcher',71907,'melanura',32.156,-115.79299999999999)
    ;
    """
    '''
    #input 2
    input2 = """
    INSERT INTO tutorial02149.bird1234 (country, duration_seconds, english_cname, id,species)
    VALUES
    ('United States',6,'Black-tailed Gnatcatcher',361929,'melanura')
    ;
    """

    start=time()
    ## enable only 1 option
    #consistency_level =ConsistencyLevel.ONE
    #consistency_level =ConsistencyLevel.QUORUM
    consistency_level =ConsistencyLevel.ALL
    ## correct the input
    query = SimpleStatement(input2,
        consistency_level=consistency_level)
    session.execute(query)
    stop=time()
    print("It took",stop-start,"(s)",sep=" ")
