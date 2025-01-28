from task import ingest_csv_file


def test_ingestion():
    msg = ingest_csv_file(
        "https://raw.githubusercontent.com/rdsea/IoTCloudSamples/master/data/bts/alarm-2017-10-23-12-vn.csv"
    )
    assert (
        msg["url"]
        == "https://raw.githubusercontent.com/rdsea/IoTCloudSamples/master/data/bts/alarm-2017-10-23-12-vn.csv"
    )
    assert msg["result"] == "OK"
