# AnnoView
Workflow for AnnoView upload

#remove ^M
sed -e "s/\r//g" slayer_annoview.csv > slayer_annoview1.csv
#add header 

#add default center
awk -F',' -v FPAT='[^,]*|("([^"]|"")*")' 'NR == FNR { keywords[$1]; next; } { if ($4 in keywords) print$0",1"; else {print $0",0"}}' accessions.txt slayer_annoview1.csv > slayer_annoview2.csv
#add header
sed '1 s/.$/Default Center/' slayer_annoview2.csv > slayer_annoview3.csv 
#write fasta if acc exist
awk -F',' -v FPAT='[^,]*|("([^"]|"")*")' 'NR>1 {if ($4) print ">"$4"\n"$9}' slayer_annoview3.csv > slayer.fasta
#remove redundant fasta sequnces
python3 rmfasta.py
#kegg
./exec_annotation -f detail-tsv -o slayer_kegg.tsv slayer1.fasta
#pfam annotation
#add kegg and pfam to csv
pfamscan.pl -fasta slayer1.fasta -dir ~/pfam/Pfam35.0 -output slayer_pfam
#merge pfams slayer_pfam1
awk '/^[^#]/ {print $1,$6}' OFS="\t" slayer_pfam | awk -F'\t' '{a[$1]=a[$1]?a[$1] OFS $2:$2} END{for (i in a) print i FS a[i]} ' OFS=" " > slayer_pfam1
#sort pfam within the same field slayer_pfam2
perl -lane 'print join ",", $F[0], sort @F[1..$#F]'  slayer_pfam1 > slayer_pfam2
sed 's/[^,]*/"&/2' slayer_pfam2 | sed 's/$/"/' > slayer_pfam3.csv
#merge pfam and kegg annotations to csv
#add headers for pfam table
sed '1i NCBI ID,PFAM' slayer_pfam3.csv > slayer_pfam4.csv
