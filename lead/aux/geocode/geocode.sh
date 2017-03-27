#!/bin/bash

psql -f aux/currbllshort/create_geocode.sql

UPDATE=0

while [[ "$UPDATE" -gt 0 ]]
do
	T="$(date +%s)"
	UPDATE=$(psql -f aux/currbllshort/geocode.sql)
	echo $UPDATE
	echo "$(($(date +%s)-T)) seconds"
	if [[ ! "$UPDATE" =~ ^UPDATE\ [0-9]*$ ]] ; then
		echo 'Unexpected output!'
		exit
	fi
	UPDATE=$(echo $UPDATE | sed 's/UPDATE //')
done

touch psql/aux/geocode