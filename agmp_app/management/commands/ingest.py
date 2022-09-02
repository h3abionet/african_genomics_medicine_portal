### run this with python manage.py ingest ./data/rawfiles/data_AGMP_clean.csv
import csv
from django.core.management.base import BaseCommand

from agmp_app.models import *


SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3

def parse_gene(header,row):
    gene_id = row[header.index('id')]
    chromosome_patch = row[header.index('chromosome')]
    gene_name = row[header.index('gene_name')]
    uniprot_id = row[header.index('uniprot')]
    gene, created = pharmacogenes.objects.get_or_create(
        # id=gene_id,
        chromosome_patch=chromosome_patch,
        gene_name=gene_name,
        uniprot_id=uniprot_id)
    if created:
        gene.save()
    return created, gene

def parse_disease(header,row):
    disease_id = row[header.index('id')]
    chromosome_patch = row[header.index('chromosome')]
    gene_name = row[header.index('gene_name')]
    uniprot_id = row[header.index('uniprot')]
    gene, created = pharmacogenes.objects.get_or_create(
        # id=gene_id,
        chromosome_patch=chromosome_patch,
        gene_name=gene_name,
        uniprot_id=uniprot_id)
    if created:
        gene.save()
    return created, gene

def parse_snp(header,row):
    snp_, created = snp.objects.get_or_create(
            rs_id = row[header.index('id')],
            gene = row[header.index('gene_name')],
            drug = row[header.index('drug_name')],
            disease = None, #row[header.index('disease')],
            allele = None, #row[header.index('allele')],
            association_with = None, #row[header.index('association_with')],
            reference = row[header.index('reference')],
            p_value = row[header.index('p_value')],
            source = row[header.index('source')],
            id_in_source = row[header.index('id_in_source')],
            region = row[header.index('region')],
            country_of_participants = row[header.index('country_of_participants')],
            latitude = row[header.index('latitude')],
            longitude = row[header.index('longitude')],
        )
    if created:
        snp_.save()
    return created, snp_





class Command(BaseCommand):
    help = (
        "Imports Drugs from a local CSV file. "
        "drug_id, drug_name, drug_bank_id, state, indication, iupac_name."
    )

    def add_arguments(self, parser):
        # Positional arguments
        parser.add_argument(
            "file_path",
            nargs=1,
            type=str,
        )
    

        
    def handle(self, *args, **options):
        verbosity = options.get("verbosity", NORMAL)
        file_path = options["file_path"][0]

        if verbosity >= NORMAL:
            self.stdout.write("=== Drugs imported ===")
        
        # with open(file_path) as f:
        #     head = f.readline().split(",")
        #     for line in f:
        #         row = line.strip().split(",")
        #         print(len(row))
        #         continue
        #         if row[0].lower().startswith("rs"):
        #             variant = snp()
        #         elif "*" in row[0]:
        #             variant = star_allele()
        
        with open(file_path) as fin:
            header = None
            rdr = csv.reader(fin, quotechar='"', delimiter=',',quoting=csv.QUOTE_ALL, skipinitialspace=True)
            for row in rdr:
                if rdr.line_num == 1:
                    header = row
                    print("\n".join(header))
                    # break
                else:
                    if row[0].startswith('rs'):
                        # try:
                            created, snp_ = parse_snp(header,row)
                            if created:
                                print(f"{snp_},{snp_.rs_id} created")
                        # except Exception as ex:
                            # print(ex)
                            
                

        # with open(file_path) as f:
        #     reader = csv.reader(f)
        #     for rownum, (drug_id, drug_name, drug_bank_id, state, indication, iupac_name) in \
        #     enumerate(reader):
        #         if rownum == 0:
        #             # let's skip the column captions
        #             continue
        #         drugs, created = \
        #         drug.objects.get_or_create(
        #             id=drug_id,
        #             drug_name=drug_name,
        #             drug_bank_id=drug_bank_id,
        #             state=state,
        #             indication=indication,
        #             iupac_name=iupac_name,
        #         )
        #         if verbosity >= NORMAL:
        #             self.stdout.write("{}. {}".format(
        #                 rownum, drug.drug_name
        #             ))
        
        