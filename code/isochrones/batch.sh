#!/bin/bash

# Edit Script Config Here
start_index=0
max_index=2
batch_size=50
max_memory=14G

cd ..
current_index=$start_index

# Keep looping through batches until you reach the max index
while [ $current_index -lt $max_index ]; do
    start_index=$current_index

    # Increase current index by batch_size
    current_index=$(expr $current_index + $batch_size)
    if [ $current_index -gt $max_index ]; then
        current_index=$max_index
    fi

    # Calculate isochrones on current batch
    echo Calculating batch: $start_index:$current_index
    python -m isochrones.calculations \
        --msoa-index="$start_index:$current_index" \
        --max-memory=$max_memory

    # Call cleanup script after each batch
    python -m isochrones.cleanup
    echo Cleaned temporary files

done
echo Completed $start_index:$max_index MSOAs