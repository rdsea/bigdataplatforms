import csv
import os
import tempfile
import urllib.request

# import urllib.request.urlretrieve
"""
this task assume that we get an CSV and store into a database.
However, we do not implement any database task. you can just do it.
Note that the assumption is that we must be able to get the file.
"""


def ingest_csv_file(url):
    # The assumpsion is to stored the file temporary in the same directory
    try:
        basename = os.path.basename(url)
        input_file = tempfile.mkdtemp() + "/" + basename
        print(f"Log: {url}")
        print("Copy data to temp file")
        urllib.request.urlretrieve(url, input_file)
        with open(input_file, encoding="utf-8") as csv_file:
            print("Process csv data")
            # No store operation has been implemented. You can implement the operation with
            # common databases.
            # You can laso just store data into files and let other components to do the storing.
            csv_reader = csv.DictReader(csv_file)
            for row in csv_reader:
                print(row)
        return {"url": url, "result": "OK"}
    except Exception as err:
        print(err)
        return {"url": url, "error": str(err)}
