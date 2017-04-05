
:::::::::::::::::::::::::::::::::::
::                               ::
::    CREATE EMPTY SQLITE DB     ::
::   leaving this here for now   ::
:::::::::::::::::::::::::::::::::::

::change to P drive and get to correct folder for inserting sqlite db

P:

cd \EPI\DATA\VitalStats\LeadProject\
sqlite3 birthtest.db ""

:::::::::::::::::::::::::::::::::::
::                               ::
::          INSERT DATA          ::
:: go to where schema8998.csv    ::
::   and schema99present.csv     ::                
:::::::::::::::::::::::::::::::::::


cd P:\EPI\DATA\VitalStats\LeadProject\


:::::::::::::::::::::::::::::::::::
::                               ::
::          INSERT DATA          ::
::                               ::
::                               ::
::Get to directory that the BTH  ::
::    files are in.              ::
:::::::::::::::::::::::::::::::::::

@echo on

:::::::::::::::::::::::::::::::::::::::::::::::::::::::
::This allows variables to be computed at execution time
::Basically helps with calculating variable values at correct time in the loop
:::::::::::::::::::::::::::::::::::::::::::::::::::::::

   SETLOCAL ENABLEDELAYEDEXPANSION

:::::::::::::::::::::::::::::::::::              
::    Loop through all records          
:::::::::::::::::::::::::::::::::::


FOR %%C in (P:\EPI\DATA\VitalStats\BTH*.*) do (

    set name=%%~nC
    set year=!name:~-2!
    echo year: !year!
    set extend=%%~nxC
    echo FILE: !extend!

:::::::::::::::::::::::::::::::::::::::::::::::::::::::
::Between 1989 and 1998?
:::::::::::::::::::::::::::::::::::::::::::::::::::::::

If !year! GTR 88 if !year! LSS 99 call :early
   
:::::::::::::::::::::::::::::::::::::::::::::::::::::::
::Between 1999 and 2009?
:::::::::::::::::::::::::::::::::::::::::::::::::::::::

IF !year! LSS 10 call :later
IF !year!==99 call :later

)

:::::::::::::::::::::::::::::::::::
::                               ::
::          Output csv file      ::
::  based on correct schema      ::
:::::::::::::::::::::::::::::::::::

:::::::::::::::::::::::::::::::::::::::::::::::::::::::
::This is a subroutine of sorts. exit /b exits subroutine and allows it to go 
:: back to where it was in the loop
:::::::::::::::::::::::::::::::::::::::::::::::::::::::
:early
   in2csv -s schema8998.csv ..\%extend% >!name!.csv
   echo EARLY: !year!
   exit /b

:later
   in2csv -s schema99present.csv ..\%extend% > !name!.csv
   echo LATE: !year!
   exit /b   