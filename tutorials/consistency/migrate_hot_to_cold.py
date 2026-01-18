# migrate_hot_to_cold_at.py
from datetime import datetime, timedelta, timezone
from cassandra.cluster import Cluster
from cassandra.auth import PlainTextAuthProvider

KEYSPACE = "tutorial12345"

def parse_cutoff(anchor_str, minutes=None, hours=None, days=None):
    # Parse anchor time as UTC (assumes "YYYY-MM-DD HH:MM[:SS]" in UTC)
    # You can include seconds; if no timezone, we treat it as UTC.
    fmt = "%Y-%m-%d %H:%M:%S" if len(anchor_str.strip().split(":")) == 3 else "%Y-%m-%d %H:%M"
    anchor = datetime.strptime(anchor_str, fmt).replace(tzinfo=timezone.utc)

    # Exactly one window should be provided
    provided = [m is not None for m in (minutes, hours, days)]
    if sum(provided) != 1:
        raise ValueError("Provide exactly one of --cutoff_minutes / --cutoff_hours / --cutoff_days")

    if minutes is not None:
        delta = timedelta(minutes=minutes)
    elif hours is not None:
        delta = timedelta(hours=hours)
    else:
        delta = timedelta(days=days)

    return anchor - delta  # move rows older than this moment

def migrate(host, username, password, city, zip_code, cutoff_dt):
    auth = PlainTextAuthProvider(username=username, password=password)
    cluster = Cluster([host], port=9042, auth_provider=auth)
    session = cluster.connect(KEYSPACE)

    # 1) Read old rows from HOT (assumes schema supports this range query)
    select_q = """
        SELECT * FROM water_hot
        WHERE city=? AND zip=? AND timestamp < ?
        ALLOW FILTERING;
    """
    rows = session.execute(select_q, (city, zip_code, cutoff_dt))

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

    print(f"[migrate] moved={moved} | cutoff_utc={cutoff_dt.isoformat()} | partition=({city},{zip_code})")
    cluster.shutdown()

if __name__ == "__main__":
    import argparse
    p = argparse.ArgumentParser(description="Move data from water_hot to water_cold using a user-chosen time window.")
    p.add_argument("--host", required=True)
    p.add_argument("--u", required=True)
    p.add_argument("--p", required=True)
    p.add_argument("--city", default="Austin")
    p.add_argument("--zip", dest="zip_code", default="78704")
    p.add_argument("--cutoff_at", required=True, help='UTC anchor time, e.g. "2026-01-18 01:30:00"')
    p.add_argument("--cutoff_minutes", type=int)
    p.add_argument("--cutoff_hours", type=float)
    p.add_argument("--cutoff_days", type=float)
    args = p.parse_args()

    cutoff_dt = parse_cutoff(args.cutoff_at, args.cutoff_minutes, args.cutoff_hours, args.cutoff_days)
    migrate(args.host, args.u, args.p, args.city, args.zip_code, cutoff_dt)
