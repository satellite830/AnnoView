
# AnnoView Upload Workflow Tutorial

AnnoView is a web server designed for exploring gene neighborhoods in bacterial and archaeal genomes. This workflow guides users through downloading gene neighborhood datasets from the NCBI for selected proteins. Additionally, it allows for the customization of AnnoView downloaded CSV files with annotations from KEGG and Pfam, and the inclusion of taxonomic information related to the genomes. 

## Installation

### Entrez Direct (EDirect)

Install Entrez Direct (EDirect) for gene neighborhood data retrieval from NCBI:

```
sh -c "$(wget -q ftp://ftp.ncbi.nlm.nih.gov/entrez/entrezdirect/install-edirect.sh -O -)"
```

Obtaining an API key from NCBI [here](https://ncbiinsights.ncbi.nlm.nih.gov/2017/11/02/new-api-keys-for-the-e-utilities/).

### PfamScan (for advanced users)

#### Install Scan 

Install PfamScan on your local machine from [here](http://ftp.ebi.ac.uk/pub/databases/Pfam/Tools/).

Then, follow the steps in the README file to install all the dependencies and the most recent Pfam databases.

Or use Conda install (this requires Conda installation)

```
conda install -c bioconda pfam_scan
```

#### Or access PfamScan using EMBL service online

Accesss PfamScan [online](https://www.ebi.ac.uk/Tools/pfa/pfamscan/). This is less recommended as EMBL PfamScan web service only allows up to 100 sequences at a time.

### KofamScan (for advanced users)

#### Install KofamScan and HMM profiles for KEGG/KO

Install KofamScan on your local machine from [here](https://www.genome.jp/ftp/tools/kofam_scan/).

Or use Conda install

```
conda install -c bioconda kofamscan
```

Download the HMM profiles for KEGG/KO with predefined score thresholds [here](https://www.genome.jp/ftp/db/kofam/).

#### Or access KofamScan using the online service

Access KOfamKoala (KofamScan service online) [here](https://www.genome.jp/tools/kofamkoala/).

## Workflow steps

### Generate a gene neighborhood dataset for proteins of your interest

Suppose you have a list of protein sequences, and you are interested in visualizing their gene neighborhood. This step allows users to download the gene neighborhood data in GBK format. 

```
bash getgbk.sh accessions.txt [length] [api_key]
```

`accessions.txt`: File containing protein accession numbers.

`length` (optional): The gene neighborhood length (default: ±10000 kb).

`api_key` (optional): Personal NCBI API key.

This script generates GenBank files for each protein accession number. Now you have a gene neighborhood dataset in GBK format that can be uploaded to AnnoView.

However, you may want more information displayed in AnnoView, e.g. taxonomic information, and functional annotations by Pfam and KEGG.

The following example shows how to retrieve those information and add them into the AnnoView downloaded CSV file, I'll be using the protein accession numbers of Slr4 proteins and their homologs as the input file

### Edit CSV (for advanced users)
This workflow is intended for editing the .csv files downloaded from AnnoView.

The slayer_annoview.csv file is downloaded from AnnoView visualization session. 

Users can add annotation categories (KEGG and Pfam), define default center gene, taxonomic information by adding these information into the table.

The updated center gene and annotation details can be viewed by uploading the updated table back to AnnoView. AnnoView will also automatically sort the gene neighborhoods when the default center gene is defined.

First, remove ^M from the .csv file. 

```
sed -e "s/\r//g" slayer_annoview.csv > slayer_annoview1.csv
```

Then, add a column of default center so AnnoView knows which gene to be based on when sorting.

```
awk -F',' -v FPAT='[^,]*|("([^"]|"")*")' 'NR == FNR { keywords[$1]; next; } { if ($4 in keywords) print$0",1"; else {print $0",0"}}' accessions.txt slayer_annoview1.csv | sed '1 s/.$/Default Center/' > slayer_annoview2.csv
```

Write the protein sequences into a fasta file.

```
awk -F',' -v FPAT='[^,]*|("([^"]|"")*")' 'NR>1 {if ($4) print ">"$4"\n"$10}' slayer_annoview2.csv > slayer.fasta
```

Remove redundant sequnces (seqeunces that are exactly the same). This line of code writes the output to slayer_unique.fasta.

```
python rmdup.py slayer.fasta
```

Annotate proteins sequences with KofamScan.

```
./exec_annotation -f detail-tsv -o slayer_kegg.tsv slayer_unique.fasta
```

Annotate protein sequences with PfamScan.

```
pfam_scan.pl -fasta slayer_unique.fasta -dir ~/pfam/Pfam35.0 -outfile slayer_pfam.txt
```

Merge Pfam annotations from the same protein sequence.

```
awk '/^[^#]/ {print $1,$6}' OFS="\t" slayer_pfam.txt | awk -F'\t' '{a[$1]=a[$1]?a[$1] OFS $2:$2} END{for (i in a) print i FS a[i]} ' OFS=" " > slayer_pfam1.txt
```

For each protein sequence, sort its Pfam annotations, edit the file into a csv table file, add column names.

```
perl -lane 'print join ",", $F[0], sort @F[1..$#F]'  slayer_pfam1.txt | sed 's/[^,]*/"&/2' | sed 's/$/"/' | sed '1i NCBI ID,PFAM' > slayer_pfam2.csv
```

Now do the same for KEGG annotations.

```
awk -F'\t' '$1 == "*"{print $2,$3}' OFS="\t" slayer_kegg.tsv > slayer_kegg1.tsv
perl -lane 'print join ",", $F[0], sort @F[1..$#F]'  slayer_kegg1.tsv | sed 's/[^,]*/"&/2' | sed 's/$/"/' | sed '1i NCBI ID,KEGG' > slayer_kegg2.csv
```

Obtain the taxonomic information for each nucleotide ID. This will generate a .csv file that contains taxonomic information from domain, phylum, class, order, family and genus. Note that this program will prompt the user for their email address that linked to NCBI, the input file name, and the output file name. The input file contains the list of nucleotide id. Here I named the output as taxa.csv.

```
# get the list of nucleotide id of the protein homologs that will be used for retrieving taxonomy information
awk -F',' 'NR>1 {print $1}' slayer_annoview1.csv | sort -u > nucleotide.txt
# get taxonomy information. The input file is nucleotide.txt, the output file is taxa.csv
python gettaxa.py
```

Merge Pfam, KEGG annotations and taxonomic information to output.csv file.

```
python merge.py slayer_annoview2.csv taxa.csv slayer_pfam2.csv slayer_kegg2.csv output.csv
```

The annoview csv, taxonomy csv and output filenames are required, but protein annotation files (Pfam & KEGG) are not necessary. Users can also use this program to merge as many protein functional annotations as they would like to the annoview download csv. For instance,

```
python merge.py slayer_annoview2.csv taxa.csv annotation1.csv annotation2.csv ... output.csv
```

Now, we have a new CSV file (output.csv) that contains not only a gene neighborhood dataset, but also its related taxonomy information, Pfam and KEGG annotations for the neighboring genes, and center gene information that can be used by AnnoView for gene neibhborhood sorting. We can now visualize the automatically sorted gene neighborhoods, and homology assignment by Pfam and KEGG in AnnoView.
