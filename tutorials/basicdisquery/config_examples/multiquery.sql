/*
There is no application-specific, semantic meaning in this example.
To have a meaningful case, you shall setup 3 related data sources  
for an application scenario and define suitable queries.
*/
SELECT 
    l.summary,
    b.country,
    trip.total_amount
FROM 
    mongodb.test.listings l, cassandra.tutorial12345.bird1234 b,
    bigquery.taxitesting.taxi_trips trip
WHERE 
    trip.VendorID = 1
LIMIT 10
