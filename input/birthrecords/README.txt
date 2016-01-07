In this folder:

A) dataTOcsv.bat : batch file to run on windows. 
    Will loop through all BTH*.* files and outputs a file BTH*.csv for each input file.

B) SCHEMAS

schema8998.csv: data dictionary with column_name, start, length for the fixed length data files between 1989 and 1998

schema99topresent.csv: data dictionary with column_name, start, length for the fixed length data files between 1999 to "present"(2009?)
         Updated schemas are now in the dssg/lead/birthrecords/
—————————
Note:  Column names are now consistent across schemas.

To be done still!!
——————————
1) Need to check the different .dat (and other extensions/other names that exist in         \VitalRecords) to get only one dataset per year
2) Re run this loop with correct schemas
3) Find 2010+ data dictionary?
