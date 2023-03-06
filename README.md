
# AnnoView upload workflow

This workflow is for users to download gene neighborhood dataset for proteins of interests in GBK format, and add customized annotations as well as taxonomy inforation to the download CSV.

## Installation

### Entrez Direct (EDirect)

Install Entrez Direct (EDirect) to retrieve gene neighborhood data from NCBI

```
sh -c "$(wget -q ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"
```

Obtaining an API key from NCBI for fasta data retrieval 

https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/

### PfamScan

To install pfamscan, 

http://ftp.ebi.ac.uk/pub/databases/Pfam/Tools/

Then, follow the steps in README to install all the dependencies and the most recent Pfam databases.

Or conda install

```
conda install -c bioconda pfam_scan
```

Accesss pfamscan online. This is least recommended as EMBL pfamscan service only allow up to 100 sequnces at a time.

https://www.ebi.ac.uk/Tools/pfa/pfamscan/

### KofamScan

Install KofamScan

https://www.genome.jp/ftp/tools/kofam_scan/

Or conda install

```
conda install -c bioconda kofamscan
```

Donwload the HMM profiles for KEGG/KO with predefined score thresholds

https://www.genome.jp/ftp/db/kofam/

Access KofamScan online

https://www.genome.jp/tools/kofamkoala/

This workflow also requires python, perl installed in your machine. 

#### To be added: orthofinder, eggnog  

## Workflow for AnnoView upload

### Generate a gene neighborhood dataset for proteins of your interest

Suppose you have a list of protein sequences, and you are interested in visualizing their gene neighborhood. The next step allows users to download the gene neighborhood data in GBK format. Note that this program will retriece the 10kb upstream and downstream regions if the length is not defined by users.

```
bash getcsv.sh accessions.txt length
```
You should have the gene neighborhood dataset in GBK format

Now, you can upload the dataset to AnnoView

However, you may want to more information to be displayed in AnnoView, e.g. taxonomic information, functional annotations by PFAM and KEGG.

In the following example, I'll be using the protein accession numbers of Slr4 proteins and its homologs as the input file

### Edit CSV 
This workflow is intended for editing the .csv files downloaded from AnnoView

Users can add annotation categories (kegg and pfam), define default center gene, taxonomic information by adding these information to the table

The updated center gene and annotation details can be viewed by uploading the updated table back to AnnoView. AnnoView will also automatically sort the gene neighborhoods when the default center gene is defined

First, remove ^M from the .csv file 

```
sed -e "s/\r//g" slayer_annoview.csv > slayer_annoview1.csv
```

Then, add a column of default center so AnnoView knows which gene to be based on when sorting

```
awk -F',' -v FPAT='[^,]*|("([^"]|"")*")' 'NR == FNR { keywords[$1]; next; } { if ($4 in keywords) print$0",1"; else {print $0",0"}}' accessions.txt slayer_annoview1.csv | sed '1 s/.$/Default Center/' > slayer_annoview2.csv
```

Write the protein sequences into a fasta file

```
awk -F',' -v FPAT='[^,]*|("([^"]|"")*")' 'NR>1 {if ($4) print ">"$4"\n"$10}' slayer_annoview2.csv > slayer.fasta
```

Remove redundant sequnces (seqeunces that are exactly the same). This program writes the output to slayer_unique.fasta

```
python rmdup.py slayer.fasta
```

Annotate proteins sequences with KofamScan

```
./exec_annotation -f detail-tsv -o slayer_kegg.tsv slayer_unique.fasta
```

Annotate protein sequences with PfamScan

```
pfam_scan.pl -fasta slayer_unique.fasta -dir ~/pfam/Pfam35.0 -outfile slayer_pfam.txt
```

Merge pfam annotations from the same protein sequence

```
awk '/^[^#]/ {print $1,$6}' OFS="\t" slayer_pfam.txt | awk -F'\t' '{a[$1]=a[$1]?a[$1] OFS $2:$2} END{for (i in a) print i FS a[i]} ' OFS=" " > slayer_pfam1.txt
```

For each protein sequence, sort its pfam annotations, edit the file into a csv table file, add column names

```
perl -lane 'print join ",", $F[0], sort @F[1..$#F]'  slayer_pfam1.txt | sed 's/[^,]*/"&/2' | sed 's/$/"/' | sed '1i NCBI ID,PFAM' > slayer_pfam2.csv
```

Now do the same for kegg annotations

```
awk -F'\t' '$1 == "*"{print $2,$3}' OFS="\t" slayer_kegg.tsv > slayer_kegg1.tsv
perl -lane 'print join ",", $F[0], sort @F[1..$#F]'  slayer_kegg1.tsv | sed 's/[^,]*/"&/2' | sed 's/$/"/' | sed '1i NCBI ID,KEGG' > slayer_kegg2.csv
```

Obtain the taxonomic information for each nucleotide ID. This will generate a .csv file that contains taxonomic information from domain, phylum, class, order, family and genus. Note that this program will prompt the user for their email address that linked to NCBI, the input file name, and the output file name. The input file contains the list of nucleotide id. Here I named the output as taxa.csv

```
# get the list of nucleotide id of the protein homologs that will be used for retrieving taxonomy information
awk -F',' '{print $1}' slayer_annoview1.csv | sort -u > nucleotide.txt
# get taxonomy information
python gettaxa.py
```

Merge pfam, kegg annotations and taxonomic information to output.csv file

```
python merge.py slayer_annoview2.csv slayer_pfam2.csv slayer_kegg2.csv taxa.csv output.csv
```

Now, we have a new CSV file (output.csv) that contains not only a gene neighborhood dataset, but also its related taxonomy information, PFAM and KEGG annotations for the neighboring genes, and center gene information that can be used by AnnoView for gene neibhborhood sorting. We can now visualize the automatically sorted gene neighborhoods, and homology assignment by PFAM and KEGG in AnnoView.
