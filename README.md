
# AnnoView Upload Workflow Tutorial

AnnoView is an online web server for gene neighborhood exploration in bacterial and archaeal genomes. This workflow provides a step-by-step guide to download gene neighborhood datasets for a list of proteins of interest from the National Center for Biotechnology Information (NCBI). Optionally, users can edit the .csv file downloaded from AnnoView, and add customized annotations in KEGG and Pfam, as well as taxonomy information of the associated genomes.

## Installation

### Entrez Direct (EDirect)

Install Entrez Direct (EDirect) for gene neighborhood data retrieval from NCBI:

```
sh -c "$(wget -q ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"
```

Obtaining an API key from NCBI [here](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/)

### PfamScan

#### Install PfamScan

Install PfamScan on your local machine from [here](http://ftp.ebi.ac.uk/pub/databases/Pfam/Tools/)

Then, follow the steps in the README file to install all the dependencies and the most recent Pfam databases.

Or use Conda install (this requires Conda installation)

```
conda install -c bioconda pfam_scan
```

#### Or access PfamScan using EMBL service online

Accesss pfamscan [online](https://www.ebi.ac.uk/Tools/pfa/pfamscan/). This is less recommended as EMBL PfamScan web service only allows up to 100 sequences at a time.

### KofamScan

#### Install KofamScan and HMM profiles for KEGG/KO

Install KofamScan on your local machine from [here](https://www.genome.jp/ftp/tools/kofam_scan/)

Or use Conda install

```
conda install -c bioconda kofamscan
```

Download the HMM profiles for KEGG/KO with predefined score thresholds [here](https://www.genome.jp/ftp/db/kofam/)

#### Or access KofamScan using the online service

Access KOfamKoala (KofamScan service online) [here](https://www.genome.jp/tools/kofamkoala/)

### Dependencies

This workflow also requires python, perl installed in your machine. 

#### To be added: orthofinder, eggnog  

## Workflow steps

### Generate a gene neighborhood dataset for proteins of your interest

Suppose you have a list of protein sequences, and you are interested in visualizing their gene neighborhood. The next step allows users to download the gene neighborhood data in GBK format. Note that this program will retrieve the 10kb upstream and downstream regions if the length is not defined by users.

```
bash getgbk.sh accessions.txt length
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

Merge pfam, kegg annotations and taxonomic information to output.csv file.

```
python merge.py slayer_annoview2.csv taxa.csv slayer_pfam2.csv slayer_kegg2.csv output.csv
```

The annoview csv, taxonomy csv and output filenames are required, but protein annotation files (PFAM & KEGG) are not necessary. Users can also use this program to merge as many protein functional annotations as they would like to the annoview download csv. For instance,

```
python merge.py slayer_annoview2.csv taxa.csv annotation1.csv annotation2.csv ... output.csv
```

Now, we have a new CSV file (output.csv) that contains not only a gene neighborhood dataset, but also its related taxonomy information, PFAM and KEGG annotations for the neighboring genes, and center gene information that can be used by AnnoView for gene neibhborhood sorting. We can now visualize the automatically sorted gene neighborhoods, and homology assignment by PFAM and KEGG in AnnoView.
