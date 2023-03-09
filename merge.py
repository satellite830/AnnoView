# the first two input files have to be the annoview csv and taxonomy csv files, the last input is the user defined output filename
# user can add PFAM, KEGG, or other annotations such as COG before the output filename, but they are not necessary

import pandas as pd
import sys

# get inputs and output file names
annoview_csv = sys.argv[1]
taxa_csv = sys.argv[2]
output_file = sys.argv[-1]

# reading csv files
dfs = []
for csv_file in sys.argv[3:-1]:
    df = pd.read_csv(csv_file)
    dfs.append(df)

# merge dataframes based on 'NCBI ID'
if len(dfs) > 0:
    output = pd.concat(dfs, sort=False).groupby('NCBI ID').first().reset_index()
else:
    output = pd.DataFrame()

# reading csv files
data1 = pd.read_csv(annoview_csv)
data2 = pd.read_csv(taxa_csv)

# merge the annoview table and taxonomy table
if not output.empty:
    output = output.merge(data1, on='NCBI ID', how='right')
    output = output.merge(data2, on='Nucleotide', how='left')
else:
    output = data1.merge(data2, on='Nucleotide', how='left')

# define the desired column order
column_order = ['Nucleotide', 'Organism', 'Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus', 'Product', 'NCBI ID', 'GENE', 'Start', 'End', 'Strand', 'CDS Length', 'Sequence', 'Default Center']

# add any missing columns to the end of the column_order list
for col in output.columns:
    if col not in column_order:
        column_order.append(col)

# reindex the DataFrame columns using the desired order
output = output.reindex(columns=column_order)

# write the merged dataframe to the output file
output.to_csv(output_file, index=False, na_rep='NA')
