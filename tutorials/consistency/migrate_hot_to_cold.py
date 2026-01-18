from datetime import datetime, timedelta
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

KEYSPACE = "tutorial123"

def migrate(host, username, password, city, zip_code, cutoff_minutes=5):
    """
    Move records older than (now - cutoff_minutes) from water_hot to water_cold
    for a single partition (city, zip). This keeps the demo simple and visible.
    """
    auth = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster([host], port=9042, auth_provider=auth)
    session = cluster.connect(KEYSPACE)

    cutoff = datetime.utcnow() - timedelta(minutes=cutoff_minutes)

    # 1) Read old data from HOT
    select_q = """
        SELECT * FROM water_hot
        WHERE city=%s AND zip=%s AND timestamp < %s ALLOW FILTERING;
    """
    rows = session.execute(select_q, (city, zip_code, cutoff))

    # 2) Insert into COLD + 3) Delete from HOT
    insert_q = session.prepare("""
        INSERT INTO water_cold (
          timestamp, city, zip, egridregion, temperaturef, humidity, data_availability_weather,
          wetbulbtemperaturef, coal, hybrid, naturalgas, nuclear, other, petroleum, solar, wind,
          data_availability_energy, onsitewuefixedapproach, onsitewuefixedcoldwater, offsitewue
        ) VALUES (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)
    """)

    delete_q = session.prepare("""
        DELETE FROM water_hot WHERE city=? AND zip=? AND timestamp=?
    """)

    moved = 0
    for r in rows:
        session.execute(insert_q, (
            r.timestamp, r.city, r.zip, r.egridregion, r.temperaturef, r.humidity,
            r.data_availability_weather, r.wetbulbtemperaturef, r.coal, r.hybrid,
            r.naturalgas, r.nuclear, r.other, r.petroleum, r.solar, r.wind,
            r.data_availability_energy, r.onsitewuefixedapproach, r.onsitewuefixedcoldwater, r.offsitewue
        ))
        session.execute(delete_q, (r.city, r.zip, r.timestamp))
        moved += 1

    print(f"[migrate] moved={moved} | cutoff={cutoff.isoformat()} UTC | partition=({city},{zip_code})")
    cluster.shutdown()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser()
    p.add_argument("--host", required=True)
    p.add_argument("--u", required=True)
    p.add_argument("--p", required=True)
    p.add_argument("--city", default="Austin")
    p.add_argument("--zip", dest="zip_code", default="78704")
    p.add_argument("--cutoff_minutes", type=int, default=5)
    args = p.parse_args()

    migrate(args.host, args.u, args.p, args.city, args.zip_code, args.cutoff_minutes)
