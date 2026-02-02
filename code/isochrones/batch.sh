#!/bin/bash

# Edit Script Config Here
start_index=0
max_index=100
batch_size=20
max_memory=20G

# Set file descriptors
exec 0</dev/null
exec 1>>batch.log
exec 2>&1

cd ..
current_index=$start_index

# Keep looping through batches until you reach the max index
while [ $current_index -lt $max_index ]; do

    # Increase current index by batch_size
    current_index=$(expr $start_index + $batch_size - 1)
    if [ $current_index -gt $max_index ]; then
        current_index=$max_index
    fi

    # Calculate isochrones on current batch
    echo Calculating batch: $start_index:$current_index
    python -m isochrones.calculations \
        --msoa-index="$start_index:$current_index" \
        --max-memory=$max_memory

    # Reset file descriptors
    exec 0</dev/null
    exec 1>>./code/batch.log
    exec 2>&1

    # Call cleanup script after each batch
    sleep 10
    python -m isochrones.cleanup
    echo Cleaned temporary files

    # Increment start index for next loop
    start_index=$(expr $current_index + 1)

done
echo Completed all MSOAs