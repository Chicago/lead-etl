This folder contains scripts for batch geocoding addresses using the PostGIS Tiger geocoder. 
We are using the city's geocoder to process currbllshort before we import the data. Therefore this code is *not* currently being used but may be useful in the future.

create_geocode.sql creates a table for geocoding and populates it with addresses for geocoding from the tests table.

geocode.sql geocodes the next batch of addresses

geocode.sh calls geocode.sql in a loop until there are no addresses left to geocode.