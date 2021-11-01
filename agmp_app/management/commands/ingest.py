from django.core.management.base import BaseCommand, CommandError
from agmp_app.models import Gene, Variant, Drug
import csv


class Command(BaseCommand):
    help = 'Closes the specified poll for voting'

    def add_arguments(self, parser):
        # parser.add_argument('genes_file','--genes_file', type=str)
        parser.add_argument(
            '--genes',
            action='store',
            dest='genes_file',
            type=str,
            help='csv file containing the genes'
        )
        parser.add_argument(
            '--drugs',
            action='store',
            dest='drugs_file',
            type=str,
            help='csv file containing the drugs'
        )
        parser.add_argument(
            '--variants',
            action='store',
            dest='variants_file',
            type=str,
            help='csv file containing the variants'
        )
        parser.add_argument(
            '--keep',
            action='store_true',
            dest='keep_entities',
            default=False,
            help='Keeps existing entities before loading',
        )

    def handle(self, *args, **options):
        if not options['keep_entities']:
            print(f"Deleting existing entities first...", end="")
            Gene.objects.all().delete()
            Variant.objects.all().delete()
            Drug.objects.all().delete()
            print(f"done.")

        # ingest Drugs
        drugs_file = options['drugs_file']
        drugs_dict = {}
        print(f"Ingesting drugs from {drugs_file}...", end="")
        rdr = csv.reader(open(drugs_file, 'r'), quotechar='"')
        head = next(rdr)
        for row in rdr:
            drug_id, drug_name, drug_bank_id, state, indication, iupac_name_or_sequence = row
            drug, created = Drug.objects.get_or_create(
                drug_id=drug_id,
                drug_name=drug_name,
                drug_bank_id=drug_bank_id,
                state=state,
                indication=indication,
                iupac_name_or_sequence=iupac_name_or_sequence)
            drugs_dict[drug_id] = drug

        # import sys
        # sys.exit()
        # ingest Genes
        genes_file = options['genes_file']
        print(f"Ingesting genes from {genes_file}...", end="")

        rdr = csv.reader(open(genes_file, 'r'), quotechar='"')
        head = next(rdr)
        for row in rdr:
            gene_id, chromosome, gene_name, uniprot_ac, function = row
            gene, created = Gene.objects.get_or_create(
                gene_name=gene_name,
                gene_id=gene_id,
                chromosome=chromosome,
                uniprot_ac=uniprot_ac,
                function=function)
        all_genes = Gene.objects.all()
        print(
            f"done.                    {all_genes.count()} Genes in the DB now")

        # ingest Variants
        variants_file = options['variants_file']
        print(f"Ingesting variants from {variants_file}...", end="")

        rdr = csv.reader(open(variants_file, 'r'))
        head = next(rdr)
        for row in rdr:
            variant_id, rs_id_star_annotation, gene_id, drug_id, phenotype_id, allele, phenotype_name, study_id, p_value, source_db, id_in_source_db, country_of_participants, geographical_region, clinical_significance, clin_var_variation_id, notes, ethnicity = row

            print(row)
            variant, created = Variant.objects.get_or_create(
                variant_id=variant_id,
                rs_id_star_annotation=rs_id_star_annotation,
                # gene_id = gene_id,
                # drug_id = drug_id,
                # phenotype_id = phenotype_id,
                allele=allele,
                # phenotype_name= phenotype_name,
                # study_id,
                source_db=source_db,
                id_in_source_db=id_in_source_db,
                # country_of_participants=country_of_participants,
                # geographical_region=geographical_region,
                clinical_significance=clinical_significance,
                clinvar_variation_id=clin_var_variation_id,
                # notes= notes,
                # ethnicity=ethnicity
            )
            # drug = drugs_dict[drug_id]
            # variant.drugs.add(drug)
            # variants.save()
        all_variants = Variant.objects.all()
        print(f"done. {all_variants.count()} Variants in the DB now")

        # make links
        for variant in Variant.objects.all():
            gene = Gene.objects.filter()

        # for line in open(genes_file):
        #     row = line.strip().split(',')
        #     print(line)
