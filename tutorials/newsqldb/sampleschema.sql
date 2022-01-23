/*
a simple example of a database schema, based on covid19 open data set
in Google Big Data
*/
CREATE DATABASE SampleCOVIDOpenData;
/*
the fields are based on the schema of the bigquery-public-data, covid19_open_data
https://cloud.google.com/bigquery/public-data
*/
CREATE TABLE SampleCOVIDOpenData.COVID19OpenData (
    location_key	STRING,
    date	DATE,
    place_id	STRING,
    country_code	STRING,
    aggregation_level	INTEGER,
    new_confirmed	INTEGER,
    new_deceased	INTEGER,
    cumulative_confirmed	INTEGER,
    cumulative_deceased	INTEGER,
    cumulative_tested	INTEGER,
    new_persons_vaccinated	INTEGER,
    cumulative_persons_vaccinated	INTEGER,
    new_persons_fully_vaccinated	INTEGER,
    cumulative_persons_fully_vaccinated	INTEGER,
    new_vaccine_doses_administered	INTEGER,
    cumulative_vaccine_doses_administered	INTEGER,
    PRIMARY KEY (country_code,place_id )
);
