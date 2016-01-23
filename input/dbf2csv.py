import sys
import csv
from dbfread import DBF

table = DBF(sys.argv[1])
writer = csv.writer(sys.stdout)

writer.writerow(table.field_names)
for record in table:
    writer.writerow(list(record.values()))
