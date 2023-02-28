import pandas as pd
import sys

# get inputs and output file names
annoview_csv = sys.argv[1]
pfam_csv = sys.argv[2]
kegg_csv = sys.argv[3]
taxa_csv = sys.argv[4]
output_file = sys.argv[5]

# reading csv files
data1 = pd.read_csv(annoview_csv)
data2 = pd.read_csv(pfam_csv)
data3 = pd.read_csv(kegg_csv)
data4 = pd.read_csv(taxa_csv)
# using merge function by setting how='left'
output = data1.merge(data2, on='NCBI ID', how='left').merge(data3, on='NCBI ID', how='left')
output2 = data4.merge(output, on='Nucleotide', how='right')

# write the merged dataframe to the output file
output2.to_csv(output_file, index=False, na_rep='NA')
