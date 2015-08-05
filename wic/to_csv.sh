#!/bin/bash
mkdir -p $OUTPUT
rm $OUTPUT/*.csv
for filename in $INPUT/*.txt; do
    echo $filename
    clinic=$(basename "$filename" .txt | sed 's/_\(I\|P\)$//')
    $INPUT2 $filename |
    sed "s/^/$clinic,/g;1s/^[^,]*,/clinic,/" |
    sed 's/[ ]\+,/,/g'  | # right strip fields
    sed 's/,\([0-9]\+\)[ ]\+\([0-9]\+\),,/,\1,\2,/g' | # ugly fix Englewood_I issues ',01   34,,' to '01,34'
    sed 's/,,\([0-9]\+\)[ ]\+\([0-9]\+\),/,\1,\2,/g' | # LowerWest_P fix ',,01  34,' to '01,34'
    tee > $OUTPUT/$(basename "$filename" .txt).csv
done
