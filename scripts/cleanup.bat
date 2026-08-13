@echo off
SETLOCAL EnableDelayedExpansion

:: Edit Script Config Here
SET max_batch=30
SET max_memory=20G
SET input_file="out/missing.txt"

:: Check if file exists
CD ..
IF EXIST %input_file% (
    ECHO Found text file containing missing indicies
) ELSE (
    ECHO Can't find file '%input_file%'
)

:: Loop through file
FOR /F "usebackq tokens=* delims=" %%F IN (%input_file%) DO (
    SET index=%%F
    ECHO Processing indicies: !index!

    :: Check if the index contains a colon
    SET temp=!index::=!
    if "!temp!"=="!index!" (

        :: Calculate single MSOA
        python -m isochrones.calculations ^
        --msoa-index=!index! ^
        --max-memory=%max_memory%

        :: Call cleanup script afterwards
        python -m isochrones.cleanup
        ECHO Cleaned temporary files
    
    ) else (

        :: If there is a range of indicies, use same batching process as batch.bat
        FOR /F "tokens=1,2 delims=:" %%A IN ("!index!") DO (
            SET current_index=%%A
            SET start_index=%%A
            SET max_index=%%B
        )
        call :batch_loop
    )
)

:: Exit script
ECHO Completed all missing indicies
EXIT /B 0

:: Define batch function
:batch_loop

:: Increase current index by max_batch size
SET /a current_index=!start_index!+%max_batch%-1
IF !current_index! GTR !max_index! (
    SET current_index=!max_index!
)

:: Calculate isochrones on current batch
ECHO Calculating batch: !start_index!:!current_index!
python -m isochrones.calculations ^
--msoa-index="!start_index!:!current_index!" ^
--max-memory=%max_memory%

:: Call cleanup script after each batch
python -m isochrones.cleanup
ECHO Cleaned temporary files

:: Increment start index for next loop
SET /a start_index=!current_index!+1

:: Go onto next batch if current_index < max_index
IF !current_index! LSS !max_index! (
    GOTO batch_loop
)

:: Finish loop
ECHO Completed all MSOAs
EXIT /B 0