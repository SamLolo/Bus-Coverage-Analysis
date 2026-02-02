@echo off
SETLOCAL EnableDelayedExpansion

:: Edit Script Config Here
SET start_index=0
SET max_index=100
SET batch_size=20
SET max_memory=20G

CD ..
SET current_index=%start_index%

:start_loop
:: Increase current index by batch_size
SET /a current_index=!start_index!+%batch_size%-1
IF !current_index! GTR %max_index% (
    SET current_index=%max_index%
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
IF !current_index! LSS %max_index% (
  GOTO start_loop
) ELSE (
  GOTO finish
)

:finish
ECHO Completed all MSOAs
EXIT /B 0