import sys
from os import path
from Bio import SeqIO

if len(sys.argv) != 2:
    print("Usage: python rmdup.py input.fasta")
    sys.exit(1)

input_file = sys.argv[1]
output_file = path.splitext(input_file)[0] + "_unique.fasta"

sequences = []
with open(output_file, "w") as output_handle:
    for record in SeqIO.parse(input_file, "fasta"):
        if str(record.seq) not in sequences:
            sequences.append(str(record.seq))
            SeqIO.write(record, output_handle, "fasta")

print("Unique sequences written to %s" % output_file)
