#!/bin/bash
# Usage: ./getgbk.sh accessions.txt [length] [api_key]
# - accessions.txt should include a list of protein accession numbers.
# - length is an optional parameter for the number of bases for neighboring genes retrieval (default is 10000).
# - api_key is an optional parameter. If not provided, a default key is used.

# IPG (Identical Protein Groups) refers to a collection of protein sequences that are identical across several species.
# This script fetches gene neighborhood information based on protein accession numbers from the IPG database.

# Check if the input file is provided
if [ "$#" -lt 1 ]; then
    echo "Usage: $0 accessions.txt [length] [api_key]"
    exit 1
fi

# Set the default length and API key if not provided
LENGTH=${2:-10000}
API_KEY=${3:-"01ab7dfc9fea43784871b15c3e85f6109e09"} # Replace with your default API key


# Read and process each line in the input file
while read -r line; do
    # Fetch IPG information for each protein
    ipg=$(efetch -db ipg -id "$line" -format ipg -api_key="$API_KEY" | awk 'FNR == 2 {print}')
    accn=$(echo "$ipg" | awk '{print $3}')

    if [[ $accn =~ N/A|skipping ]]; then
        echo "$line does not have gene neighborhood information"
    else
        echo "$ipg" >> ipg.txt
    fi
done < "$1"

# Process the IPG information and fetch GenBank files
while IFS=$'\t' read -r id source accn start stop strand aa product organism strain assembly; do
    stop=$((start + LENGTH))
    start=$((start - LENGTH))
    [ "$start" -lt 0 ] && start=0

    # Fetch genbank files for the gene neighborhoods
    rslt=$(efetch -db nuccore -id "$accn" -format gb -seq_start "$start" -seq_stop "$stop" -api_key="$API_KEY" < /dev/null)
    echo "$rslt" >> "$aa".gbk
done < ipg.txt
