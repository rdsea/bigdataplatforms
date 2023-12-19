import os
import tempfile
import csv
import urllib.request
import socket

socket.setdefaulttimeout(5)

'''
This task assumes that we get a CSV and store it in a database.

However, we do not implement a database task, you can just do it.

Note that the assumption is that we must be able to get the file.
'''


def ingest_csv_file(url):
    '''
        It is assumed that the file is stored in a new temporary directory.
    '''
    try:
        basename = os.path.basename(url)
        input_file = tempfile.mkdtemp() + '/' + basename
        print("Log: ", url)
        print("Copy data to temp file")

        '''
        Add headers to prevent "<urlopen error [Errno 111] Connection refused>"
        '''
        opener = urllib.request.build_opener()
        opener.addheaders = [('User-agent', 'Mozilla/5.0')]
        urllib.request.install_opener(opener)
        urllib.request.urlretrieve(url, input_file)

        with open(input_file, encoding='utf-8') as csv_file:
            print("Process csv data")
            '''
            No store operation has been implemented. You can implement the operation with common databases.
            You can also just store data into files and let other components to do the storing.
            '''
            csvReader = csv.DictReader(csv_file)
            for row in csvReader:
                print(row)
        return {"url": url, "result": "OK"}
    except Exception as err:
        print(err)
        return {"url": url, "error": str(err)}
