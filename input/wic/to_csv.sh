#!/bin/bash
mkdir -p $OUTPUT
rm $OUTPUT/*.txt
for filename in $INPUT/*_I.txt; do
    echo $filename
    clinic=$(basename "$filename" .txt | sed 's/_I$//')
    $INPUT2 $filename |
    sed 's/[ ]\+,/,/g'  | # right strip fields
    sed 's/,\([0-9]\+\)[ ]\+\([0-9]\+\),,/,\1,\2,/g' | # ugly fix Englewood issues
    awk -v clinic="$clinic" 'BEGIN {FS = OFS = ","} {NF=13; $13=clinic; print}' > $OUTPUT/$(basename "$filename")
done
# LowerWest has first and last name columns switched :(
awk 'BEGIN {FS = OFS = ","} {t = $1; $1 = $2; $2 = t; print;}' $OUTPUT/LowerWest_I.txt > $OUTPUT/tmp && mv $OUTPUT/tmp $OUTPUT/LowerWest_I.txt 
# Englewood switched zip address dob
awk 'BEGIN {FS = OFS = ","} {t = $3; $3 = $4; $4 = $5; $5 = t; print;}' $OUTPUT/Englewood_I.txt > $OUTPUT/tmp && mv $OUTPUT/tmp $OUTPUT/Englewood_I.txt 

