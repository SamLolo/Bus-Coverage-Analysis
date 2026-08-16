#!/bin/bash

# Edit Script Config Here
max_batch=25
max_memory=20G
input_file="data/raw/sampled_lsoas.csv"

# Check if file exists
cd ..
if [ -f "$input_file" ]; then
    echo "Found input file"
else
    echo "Can't find file '$input_file'"
    exit 1
fi

# Initialise batch variables
count=0
lsoa_batch=
total_count=0

# Loop through file, skipping the header row
while IFS=',' read -r id name; do

    # Add id to the current batch
    if [ -z "$lsoa_batch" ]; then
        lsoa_batch="$id"
    else
        lsoa_batch="$lsoa_batch,$id"
    fi
    count=$((count + 1))
    total_count=$((total_count + 1))

    # When batch reaches max batch size, process it
    if [ "$count" -eq "$max_batch" ]; then
        echo "Running batch: $lsoa_batch"

        # Calculate LSOAs
        python -m isochrones.lsoas \
            --lsoa-ids="$lsoa_batch" \
            --max-memory="$max_memory"

        # Call cleanup script afterwards
        python -m isochrones.cleanup
        echo "Cleaned temporary files"

        # Reset variables
        echo "Completed $count LSOAs ($total_count total)"
        count=0
        lsoa_batch=
    fi
done < <(tail -n +2 "$input_file")

# Process any remaining IDs that didn't fill a full batch
if [ -n "$lsoa_batch" ]; then
    echo "Running batch: $lsoa_batch"

    # Calculate LSOAs
    python -m isochrones.lsoas \
        --lsoa-ids="$lsoa_batch" \
        --max-memory="$max_memory"

    # Call cleanup script afterwards
    python -m isochrones.cleanup
    echo "Cleaned temporary files"
fi

# Exit script
echo "Completed all $total_count LSOA samples"
exit 0
