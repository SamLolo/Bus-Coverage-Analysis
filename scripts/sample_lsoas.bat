@echo off
SETLOCAL EnableDelayedExpansion

:: Edit Script Config Here
SET max_batch=25
SET max_memory=20G
SET input_file="data/raw/sampled_lsoas.csv"

:: Check if file exists
CD ..
IF EXIST %input_file% (
    ECHO Found input file
) ELSE (
    ECHO Can't find file '%input_file%'
)

:: Initialise batch variables
SET count=0
SET lsoa_batch=
SET total_count=0

:: Loop through file, skipping the header row
FOR /F "usebackq skip=1 tokens=1 delims=," %%F IN (%input_file%) DO (
    SET id=%%F

    :: Add id to the current batch
    IF "!lsoa_batch!"=="" (
        SET lsoa_batch=!id!
    ) ELSE (
        SET lsoa_batch=!lsoa_batch!,!id!
    )
    SET /a count+=1
    SET /a total_count+=1

    :: When batch reaches max batch size, process it
    IF !count! EQU %max_batch% (
        ECHO Running batch: !lsoa_batch!

        :: Calculate LSOAs
        python -m isochrones.lsoas ^
        --lsoa-ids=!lsoa_batch! ^
        --max-memory=%max_memory%

        :: Call cleanup script afterwards
        python -m isochrones.cleanup
        ECHO Cleaned temporary files

        :: Reset variables
        ECHO Completed !count! LSOAs ^(!total_count! total^)
        SET count=0
        SET lsoa_batch=
    
    )
)

:: Process any remaining IDs that didn't fill a full batch
IF NOT "!lsoa_batch!"=="" (
    ECHO Running batch: !lsoa_batch!
    
    :: Calculate LSOAs
    python -m isochrones.lsoas ^
    --lsoa-ids=!lsoa_batch! ^
    --max-memory=%max_memory%

    :: Call cleanup script afterwards
    python -m isochrones.cleanup
    ECHO Cleaned temporary files

)

:: Exit script
ECHO Completed all !total_count! LSOA samples
EXIT /B 0