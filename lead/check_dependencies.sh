#!/bin/bash

# check command line dependencies
names=( drake mdb-tools ogr2ogr shp2pgsql "PostgreSQL client")
commands=( "drake" "mdb-ver" "ogr2ogr" "shp2pgsql" "psql")
versions=( "--version 2>/dev/null" "-M" "--version" "" "--version")
for ((i=0; i < ${#names[@]}; i++))
do
    if command -v ${commands[i]} >/dev/null 2>&1 ; then
        echo "FOUND: ${names[i]}, version: $(${commands[i]} ${versions[i]} 2>/dev/null | head -n 1)"
    else
        echo "ERROR: ${names[i]} not found"
    fi
done

# read database profile
PROFILE="${PROFILE:default_profile}"
set -a && source default_profile
PSQL="psql -t -A -q "

# check database dependencies
extension_template="select installed_version from pg_available_extensions where name="
psql_deps=( "server" "extension postgis" "extension unaccent" ) 
extension_queries=( "SHOW server_version" "$extension_template'postgis'" "$extension_template'unaccent'")
for (( i=0; i < ${#psql_deps[@]}; i++ ))
do
    version=$(echo ${extension_queries[i]} | $PSQL 2>/dev/null)
    if [[ $version ]]; then
        echo "FOUND: PostgreSQL ${psql_deps[i]}, version: $version"
    else
        echo "ERROR: PostgreSQL ${psql_deps[i]} not found"
    fi
done

# check if python can successfully write and read and HDF file
tmpfile=$(mktemp)
if python check_hdf.py $tmpfile ; then
    echo "FOUND: Python pandas HDF support"
else
    echo "ERROR: Python pandas failed to read/write HDF"
fi
