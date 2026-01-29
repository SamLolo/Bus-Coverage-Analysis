@echo off
SETLOCAL EnableDelayedExpansion

:: Edit Script Config Here
SET start_index=6166
SET max_index=6300
SET batch_size=10
SET max_memory=14G

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
ECHO Completed %start_index%:%max_index% MSOAs
EXIT /B 0