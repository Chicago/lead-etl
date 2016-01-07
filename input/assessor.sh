#!/bin/bash

file="/glusterfs/users/erozier/data/assessor.mdb"

# create table in input schema, call it assessor, replace col spaces with underscores
mdb-schema -N input $file postgres | 
	sed 's/Cookcounty land bank14/assessor/' | 
	awk -F\" '{OFS="\"";for(i=2;i<NF;i+=2)gsub(/ /,"_",$i);print}' | 
	psql

mdb-export $file "Cookcounty land bank14" | psql -c "\copy input.assessor from stdin with csv header"
