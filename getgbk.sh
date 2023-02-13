#!/bin/bash
#usage: bash getgbk.sh file length
#the input file should be a list of protein accession numbers

#efetch ipg information for each protein
#this script only fetch the first genome with the protein
while read line; do
ipg=`efetch -db ipg -id "$line" -format ipg -api_key="01ab7dfc9fea43784871b15c3e85f6109e09" | awk 'FNR == 2 {print}'`
accn=$(echo $ipg | awk '{print $3}')
echo "$accn"
if [[ $accn =~ N/A|skipping ]]; then
	echo "$line does not have gene neighborhood information"
else
	echo "$ipg" >> ipg.txt
fi
done < $1

#allow customized length for neighboring genes retrieval
bases=10000
if [ -n "$2" ]; then
	bases=$2
fi

#efetch genbank files
while IFS=$'\t' read -r id source accn start stop strand aa product organism strain assembly; do
stop=$(( $start + $bases ))
start=$(( $start - $bases))
if [ "$start" -lt 0 ] ; then
	start=0
fi
#echo $start"\t"$stop >> pos.txt
#if [ "$strand" = "-" ] ; then
#	rslt=`efetch -db nuccore -id $accn -format gb -seq_start $start -seq_stop $stop -revcomp -api_key="01ab7dfc9fea43784871b15c3e85f6109e09" < /dev/null`
#else
	rslt=`efetch -db nuccore -id $accn -format gb -seq_start $start -seq_stop $stop -api_key="01ab7dfc9fea43784871b15c3e85f6109e09" < /dev/null`
#fi
echo "$rslt" >> "$aa".gbk
done < ipg.txt
