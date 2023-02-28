from Bio import Entrez, SeqIO
import csv

def get_taxonomic_info(nucleotide_ids, email):
    Entrez.email = email
    taxonomic_info = []
    for nucleotide_id in nucleotide_ids:
        handle = Entrez.efetch(db='nucleotide', id=nucleotide_id, rettype='gb', retmode='text')
        record = SeqIO.read(handle, 'genbank')
        handle.close()
        for feature in record.features:
            if feature.type == 'source':
                taxonomy = feature.qualifiers.get('db_xref', [])
                for item in taxonomy:
                    if 'taxon:' in item:
                        tax_id = item.replace('taxon:', '')
                        taxon_info = Entrez.efetch(db="taxonomy", id=tax_id, retmode="xml")
                        taxon_record = Entrez.read(taxon_info)
                        lineage = taxon_record[0]['LineageEx']
                        domain = phylum = klass = order = family = genus = ''
                        for lin_item in lineage:
                            if lin_item['Rank'] == 'superkingdom':
                                domain = lin_item['ScientificName']
                            elif lin_item['Rank'] == 'phylum':
                                phylum = lin_item['ScientificName']
                            elif lin_item['Rank'] == 'class':
                                klass = lin_item['ScientificName']
                            elif lin_item['Rank'] == 'order':
                                order = lin_item['ScientificName']
                            elif lin_item['Rank'] == 'family':
                                family = lin_item['ScientificName']
                            elif lin_item['Rank'] == 'genus':
                                genus = lin_item['ScientificName']
                        taxonomic_info.append([nucleotide_id, domain, phylum, klass, order, family, genus])
    return taxonomic_info

email = input("Enter your email address for the Entrez service: ")
input_file = input("Enter the path to the input file: ")
output_file = input("Enter the path to the output file: ")

with open(input_file) as f:
    nucleotide_ids = [line.strip() for line in f]

taxonomic_info = get_taxonomic_info(nucleotide_ids, email)

with open(output_file, 'w', newline='') as csvfile:
    writer = csv.writer(csvfile)
    writer.writerow(['Nucleotide', 'Domain', 'Phylum', 'Class', 'Order', 'Family', 'Genus'])
    writer.writerows(taxonomic_info)

print("Taxonomic information written to %s" % output_file)

