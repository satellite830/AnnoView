
# AnnoView upload workflow

This workflow is for users to create gene neighborhood dataset in GBK format.

## Installation

To use PfamScan and KofamScan on local machine, installation of the database is also required 

### Entrez Direct (EDirect)

Install Entrez Direct (EDirect) to retrieve gene neighborhood data from NCBI

```
sh -c "$(wget -q ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"
```

Obtaining an API key from NCBI for fasta data retrieval 

https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/

### PfamScan

You can access PfamScan online, or download PfamScan in your own local machine for 

Accesss pfamscan online

https://www.ebi.ac.uk/Tools/pfa/pfamscan/

To install pfamscan, dow

http://ftp.ebi.ac.uk/pub/databases/Pfam/Tools/

Or conda install

```
conda install -c bioconda pfam_scan
```

pros and cons for pfamscan online
pros easy access
cons slower speed? limited number of queries?
How about pfamscan api?

why download pfamscan in local machine / choose the pfam version? 


### KofamScan

Access KofamScan online

https://www.genome.jp/tools/kofamkoala/

Install KofamScan

https://www.genome.jp/ftp/tools/kofam_scan/

Or conda install

```
conda install -c bioconda kofamscan
```

#### To be added: orthofinder, eggnog 

These installation may require storage for the database   

## Workflow for AnnoView upload

### Generate a gene neighborhood dataset for proteins of your interest

Suppose you have a list of protein sequences, and you are interested in visualizing their gene neighborhood

```
bash getcsv.sh length
```
You should have the gene neighborhood dataset in GBK format

Now, you can upload the dataset to AnnoView

However, you may want to more information to be displayed in AnnoView, e.g. taxonomic information, functional annotations by PFAM and KEGG.

### Edit CSV 
This workflow is intended for editing the .csv files downloaded from AnnoView

Users can add annotation categories (kegg and pfam), define default center gene, taxonomic information by adding these information to the table

The updated center gene and annotation details can be viewed by uploading the updated table back to AnnoView. AnnoView will also automatically sort the gene neighborhoods when the default center gene is defined

First, remove ^M from the .csv file 

```
sed -e "s/\r//g" slayer_annoview.csv > slayer_annoview1.csv
```

Then, add column of default center so AnnoView knows which gene to be based on when sorting

```
awk -F',' -v FPAT='[^,]*|("([^"]|"")*")' 'NR == FNR { keywords[$1]; next; } { if ($4 in keywords) print$0",1"; else {print $0",0"}}' accessions.txt slayer_annoview1.csv > slayer_annoview2.csv
sed '1 s/.$/Default Center/' slayer_annoview2.csv > slayer_annoview3.csv
```

Write protein sequences into a fasta file

```
awk -F',' -v FPAT='[^,]*|("([^"]|"")*")' 'NR>1 {if ($4) print ">"$4"\n"$9}' slayer_annoview3.csv > slayer.fasta
```

Remove redundant sequnces (seqeunces that are exactly the same) 

```
python rmdup.py slayer.fasta
```

Annotate proteins sequences with KofamScan

```
./exec_annotation -f detail-tsv -o slayer_kegg.tsv slayer1.fasta
```

Annotate protein sequences with PfamScan

```
pfamscan.pl -fasta slayer1.fasta -dir ~/pfam/Pfam35.0 -output slayer_pfam
```

Merge pfam annotations from the same protein sequence

```
awk '/^[^#]/ {print $1,$6}' OFS="\t" slayer_pfam | awk -F'\t' '{a[$1]=a[$1]?a[$1] OFS $2:$2} END{for (i in a) print i FS a[i]} ' OFS=" " > slayer_pfam1.csv
```

For each protein sequence, sort its pfam annotations

```
perl -lane 'print join ",", $F[0], sort @F[1..$#F]'  slayer_pfam1.csv > slayer_pfam2.csv
sed 's/[^,]*/"&/2' slayer_pfam2.csv | sed 's/$/"/' > slayer_pfam3.csv
```

Add a header for pfam table   

```
sed '1i NCBI ID,PFAM' slayer_pfam3.csv > slayer_pfam4.csv   
```

Now do the same for kegg annotations

```
awk '/^[^#]/ {print $1,$6}' OFS="\t" slayer_kegg.tsv
perl -lane 'print join ",", $F[0], sort @F[1..$#F]'  slayer_pfam1.csv > slayer_pfam2.csv
sed 's/[^,]*/"&/2' slayer_pfam2.csv | sed 's/$/"/' > slayer_pfam3.csv
```

Obtain the taxonomic information for each nucleotide ID. This will generate a .csv file that contains taxonomic information from domain, phylum, class, order, family and genus. Note that this program will prompt the user for their email address that linked to NCBI, the input file name, and the output file name. Here I named the output as taxa.csv

```
python gettaxa.py
```

Merge pfam, kegg annotations and taxonomic information to csv   

```
python merge.py
```

Now, we have a new CSV file that contains not only a gene neighborhood dataset, but also its related taxonomic information and PFAM and KEGG annotations for the neighboring genes. We can now visualize the homology assignment by PFAM and KEGG in AnnoView.
