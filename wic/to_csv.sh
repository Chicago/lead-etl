#!/bin/bash
mkdir -p $OUTPUT
rm $OUTPUT/*.txt
for filename in $INPUT/*_I.txt; do
    echo $filename
    clinic=$(basename "$filename" .txt | sed 's/_I$//')
    $INPUT2 $filename |
    sed 's/[ ]\+,/,/g'  | # right strip fields
    sed 's/,\([0-9]\+\)[ ]\+\([0-9]\+\),,/,\1,\2,/g' | # ugly fix Englewood issues
    awk -v clinic="$clinic" 'BEGIN {FS = OFS = ","} {NF=13; if (NR != 1) { $13=clinic } else { $13="clinic"; $12="pa_c5";$11="pa_c4";$10="pa_c3";$9="pa_c2";$8="pa_c1"}; print}' > $OUTPUT/$(basename "$filename")
done
