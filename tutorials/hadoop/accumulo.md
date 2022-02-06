## Apache Accumulo

This example illustrates the example using Apache Accumulo.

## Accumulo setup

We assume that you will use Hadoop File System as the storage for Accumulo. The start guide of Accumulo gives a very straightforward setup for a cluster of Accumulo (single machine): https://accumulo.apache.org/docs/2.x/getting-started/quickstart

## Data

We use the bird data from: [Avian Vocalizations from CA & NV, USA](https://www.kaggle.com/samhiatt/xenocanto-avian-vocalizations-canv-usa)

## Set of commands

The list of commands can be executed via HBase shell, e.g.,
```
$ /opt/accumulo/bin/accumulo shell -u root
...
hbase:001:0> create  'hbird0', 'birdinfo', 'songinfo', 'location', 'record'
Created table hbird0
Took 2.5814 seconds
=> Hbase::Table - hbird0

```
### Create a table

Create a table:

```
createtable hbird0
```
### Simple inserts

A set of simple INSERT statements to create some rows:
* Follow the rule:
   ```
    usage: insert <row> <colfamily> <colqualifier> <value> [-?] [-d <arg>] [-l <expression>] [--timeout <timeout>] [-ts <timestamp>]
   ```
* We dont set timestamp
* We set visibility to two different groups: "datascientist" and "students"

#### Some inserts with the visibility "datascientists"

```
insert "17804" "birdinfo" "country" "United States" -l "datascientist"
insert "17804" "birdinfo" "english_cname" "Aberts Towhee" -l "datascientist"
insert "17804"  "songinfo" "duration" 3 -l "datascientist"
insert "17804"  "songinfo" "file_id"  17804 -l "datascientist"
insert "17804" "songinfo" "file_name" "XC17804.mp3" -l "datascientist"
insert "17804" "songinfo" "file_url" "https://www.xeno-canto.org/17804/download" -l "datascientist"
insert "17804" "birdinfo" "species" "aberti" -l "datascientist"
insert "17804" "location" "point" (33.3117,-114.68911999999999) -l "datascientist"
insert "17804" "location" "place" "Cibola National Wildlife Refuge, Cibola, Arizona, United States" -l "datascientist"
insert "17804" "record" "recordist" "Nathan Pieplow" -l "datascientist"
insert "17804" "record" "recordist_url" "https://www.xeno-canto.org/contributor/EKKJJJRDJY" -l "datascientist"
insert "17804" "record" "sonogram_url" "https://www.xeno-canto.org/sounds/uploaded/EKKJJJRDJY/ffts/XC17804-med.png" -l "datascientist"
```
#### Some inserts with the visibility "datascientists"

```
insert "71852" "birdinfo" "country" "Mexico" -l "students"
insert "71852" "songinfo" "duration" 28 -l "students"
insert "71852" "birdinfo" "english_cname" "Ash-throated Flycatcher" -l "students"
insert "71852" "songinfo" "file_id" 71852 -l "students"
insert "71852" "birdinfo" "species" "cinerascens" -l "students"
insert "71852" "location" "point" (32.156,-115.79299999999999) -l "students"


```
#### Check the  data:
First make sure the current user ("root") is with the authorization of seeing "datascientist" visibility constraints. Then scan the data:
```
root@accumulop620 hbird0> setauths -u root -s datascientist
root@accumulop620 hbird0> scan
17804 birdinfo:country [datascientist]    United States
17804 birdinfo:english_cname [datascientist]    Aberts Towhee
17804 birdinfo:species [datascientist]    aberti
17804 location:place [datascientist]    Cibola National Wildlife Refuge, Cibola, Arizona, United States
17804 location:point [datascientist]    (33.3117,-114.68911999999999)
17804 record:recordist [datascientist]    Nathan Pieplow
17804 record:recordist_url [datascientist]    https://www.xeno-canto.org/contributor/EKKJJJRDJY
17804 record:sonogram_url [datascientist]    https://www.xeno-canto.org/sounds/uploaded/EKKJJJRDJY/ffts/XC17804-med.png
17804 songinfo:duration [datascientist]    3
17804 songinfo:file_id [datascientist]    17804
17804 songinfo:file_name [datascientist]    XC17804.mp3
17804 songinfo:file_url [datascientist]    https://www.xeno-canto.org/17804/download
```

Make sure the current user ("root") is with the authorization of seeing "students" visibility constraints. Then scan the data:

```
root@accumulop620 hbird0> setauths -u root -s students
root@accumulop620 hbird0> scan
71852 birdinfo:country [students]    Mexico
71852 birdinfo:english_cname [students]    Ash-throated Flycatcher
71852 birdinfo:species [students]    cinerascens
71852 location:point [students]    (32.156,-115.79299999999999)
71852 songinfo:duration [students]    28
71852 songinfo:file_id [students]    71852
```

 You can practice to put a lot of data and run analytics/queries.
