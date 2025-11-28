from cassandra.cluster import Cluster
import os

CASSANDRA_HOSTS = os.getenv("CASSANDRA_HOST", "127.0.0.1").split(",")
CASSANDRA_KEYSPACE = os.getenv("CASSANDRA_KEYSPACE", "online_edu")

_cluster = None
_session = None

def get_cassandra_session():
    global _session, _cluster
    if _session is None:
        _cluster = Cluster(CASSANDRA_HOSTS)
        _session = _cluster.connect(CASSANDRA_KEYSPACE)
    return _session