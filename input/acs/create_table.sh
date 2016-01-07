#!/bin/bash

filename=$1
tablename=`basename $filename | sed 's/_with_ann.csv//'`

cat <( echo "DROP TABLE IF EXISTS input.$tablename; create table input.$tablename (" ) \
<( head -n 1 $filename | sed -f input/acs/create_table.sed ) \
<( echo ' decimal);')