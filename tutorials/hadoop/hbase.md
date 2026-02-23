## HBase Example

This example illustrates the example of HBase we discuss in the lecture.

## HBase setup

You can use your local installation (standalone or psuedo-distributed one)

## Data

We use the bird data from: [Avian Vocalizations from CA & NV, USA](https://www.kaggle.com/samhiatt/xenocanto-avian-vocalizations-canv-usa)

## Set of commands
The list of commands can be executed via HBase shell, e.g.,
```
$ /opt/hbase/bin/hbase shell
...
hbase:001:0> create  'hbird0', 'birdinfo', 'songinfo', 'location', 'record'
Created table hbird0
Took 2.5814 seconds
=> Hbase::Table - hbird0

```
Create a table with a set of column familities:

```
create  'hbird0', 'birdinfo', 'songinfo', 'location', 'record'
```

A set of simple PUT statements to create some rows:

```
put 'hbird0', '17804',

put 'hbird0', '17804','birdinfo:country', 'United States'

put 'hbird0', '17804','birdinfo:english_cname','Aberts Towhee'

put 'hbird0', '17804','songinfo:duration',3

put 'hbird0', '17804','songinfo:file_id', 17804

put 'hbird0', '17804','songinfo:file_name', 'XC17804.mp3'

put 'hbird0', '17804','songinfo:file_url':"https://www.xeno-canto.org/17804/download"

put 'hbird0', '17804','birdinfo:species':'aberti'

put 'hbird0', '17804','location:latitude':33.3117

put 'hbird0', '17804','location:longitude':-114.68911999999999

put 'hbird0', '17804','location:place':'Cibola National Wildlife Refuge, Cibola, Arizona, United States'

put 'hbird0', '17804','record:recordist':'Nathan Pieplow'

put 'hbird0', '17804','record:recordist_url':"https://www.xeno-canto.org/contributor/EKKJJJRDJY"

put 'hbird0', '17804','record:sonogram_url':"https://www.xeno-canto.org/sounds/uploaded/EKKJJJRDJY/ffts/XC17804-med.png"

put 'hbird0', '71852', 'birdinfo:country','Mexico'
put 'hbird0', '71852', 'songinfo:duration', 28
put 'hbird0', '71852', 'birdinfo:english_cname', 'Ash-throated Flycatcher'
put 'hbird0', '71852', 'songinfo:file_id',71852
put 'hbird0', '71852', 'birdinfo:species', 'cinerascens'
put 'hbird0', '71852', 'location:latitude', 32.156
put 'hbird0', '71852', 'location:longitude', -115.79299999999999

```
Check the  data:

```
scan 'hbird0'

```
The result would be:
```
hbase:038:0> scan 'hbird0'
ROW                              COLUMN+CELL
 17804                           column=birdinfo:english_cname, timestamp=2022-02-05T11:56:09.114, value=Aberts Towhee
 17804                           column=songinfo:duration, timestamp=2022-02-05T11:56:09.154, value=3
 17804                           column=songinfo:file_id, timestamp=2022-02-05T11:56:09.178, value=17804
 17804                           column=songinfo:file_name, timestamp=2022-02-05T11:56:09.205, value=XC17804.mp3
 71852                           column=birdinfo:country, timestamp=2022-02-05T11:56:09.415, value=Mexico
 71852                           column=birdinfo:english_cname, timestamp=2022-02-05T11:56:09.445, value=Ash-throated Flycatc
                                 her
 71852                           column=birdinfo:species, timestamp=2022-02-05T11:56:09.488, value=cinerascens
 71852                           column=location:latitude, timestamp=2022-02-05T11:56:09.504, value=32.156
 71852                           column=location:longitude, timestamp=2022-02-05T11:56:12.253, value=-115.79299999999999
 71852                           column=songinfo:duration, timestamp=2022-02-05T11:56:09.430, value=28
 71852                           column=songinfo:file_id, timestamp=2022-02-05T11:56:09.459, value=71852
2 row(s)
Took 0.0206 seconds
```

You can practice to put a lot of data and run analytics/queries.
