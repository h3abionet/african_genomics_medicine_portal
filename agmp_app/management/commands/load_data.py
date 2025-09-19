import csv
import os
import logging
import numpy as np
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from django.db import connection, transaction
from django.core.management.base import BaseCommand
from agmp_app.models import Variantagmp, Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, VariantStudyagmp

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

# Load environment variables from .env file
load_dotenv()

class Command(BaseCommand):
    help = 'Imports data from CSV and Excel files into the database'

    def add_arguments(self, parser):
        parser.add_argument(
            '--skip-delete',
            action='store_true',
            help='Skip deleting existing data before import',
        )
        parser.add_argument(
            '--first-file',
            type=str,
            help='Path to the first CSV file',
        )
        parser.add_argument(
            '--second-file',
            type=str,
            help='Path to the second Excel file',
        )

    def handle(self, *args, **options):
        """
        Main function to load data into the database.
        Reads from CSV and Excel files and populates the database tables.
        Uses environment variables for database configuration.
        """
        try:
            # Test database connection
            with connection.cursor() as cursor:
                cursor.execute("SELECT 1")
                result = cursor.fetchone()
            self.stdout.write(self.style.SUCCESS(f"Database connection successful: {result}"))
            self.stdout.write(self.style.SUCCESS(f"Using database: {os.environ.get('DB_NAME')} on host: {os.environ.get('DB_HOST')}"))
            
            # Get base directory and file paths
            base_dir = Path(__file__).resolve().parent.parent.parent.parent
            
            # Use command line arguments if provided, otherwise use default paths
            first_import_path = Path(options['first_file']) if options.get('first_file') else base_dir / 'import_csv' / 'first_import_job_run.csv'
            second_import_path = Path(options['second_file']) if options.get('second_file') else base_dir / 'import_csv' / 'second_import_job_run_april_2025.xlsx'
            
            self.stdout.write(f"First import file path: {first_import_path}")
            self.stdout.write(f"Second import file path: {second_import_path}")
            
            # Check if files exist
            if not first_import_path.exists():
                self.stdout.write(self.style.ERROR(f"First import file not found: {first_import_path}"))
                return
            
            if not second_import_path.exists():
                self.stdout.write(self.style.ERROR(f"Second import file not found: {second_import_path}"))
                return
            
            with transaction.atomic():
                # Delete all existing data if not skipped
                if not options['skip_delete']:
                    self.stdout.write("Deleting existing data...")
                    Variantagmp.objects.all().delete()
                    Drugagmp.objects.all().delete()
                    Geneagmp.objects.all().delete()
                    Studyagmp.objects.all().delete()
                    Phenotypeagmp.objects.all().delete()
                    VariantStudyagmp.objects.all().delete()
                    self.stdout.write(self.style.SUCCESS("All existing data deleted."))
                
                # Process first import file
                self.process_first_import(first_import_path)
                
                # Process second import file
                self.process_second_import(second_import_path)
                
                # Print final statistics
                self.print_statistics()
                
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during data import: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise

    def normalize_value(self, value):
        """Normalize p-values replacing NS, ns, and nan with NR"""
        if pd.isna(value) or value in ['NS', 'ns', 'nan']:
            return 'NR'
        return value

    def process_first_import(self, file_path):
        """Process the first CSV import file"""
        self.stdout.write("Starting first import job...")
        
        try:
            # Import the first file
            df_csv = pd.read_csv(file_path, encoding='latin-1')
            self.stdout.write(self.style.SUCCESS(f"Loaded {len(df_csv)} rows from first import file"))
            
            count = 0
            for index, row in df_csv.iterrows():
                try:
                    p, created = Phenotypeagmp.objects.get_or_create(name=row['phenotype'])
                    s, created = Studyagmp.objects.get_or_create(
                        data_ac=row['data_ac'], 
                        publication_id=row['publication'], 
                        publication_year=row['publication_year'], 
                        study_type=row['study_type'], 
                        title=row['title']
                    )
                    d, created = Drugagmp.objects.get_or_create(
                        drug_bank_id=row['ID Drug bank'], 
                        drug_name=row['drug_name'], 
                        indication=row['Indication'], 
                        state=row['state'], 
                        iupac_name_seq=row['IUPAC_name']
                    )
                    g, created = Geneagmp.objects.get_or_create(
                        gene_name=row['gene_name'], 
                        gene_id=row['curated_gene_symbol'], 
                        chromosome=row['chromosome'], 
                        uniprot_ac=row['uniprot'], 
                        function=row['function']
                    )
                    v = Variantagmp(
                        studyagmp=s, 
                        drugagmp=d, 
                        phenotypeagmp=p, 
                        geneagmp=g, 
                        variant_type=row['variant_type'], 
                        source_db=row['source'], 
                        id_in_source_db=row['id_in_source'], 
                        rs_id=row['id']
                    )
                    v.save()

                    normalized_01_p_value = self.normalize_value(row['p-value'])

                    vs = VariantStudyagmp(
                        studyagmp=s, 
                        variantagmp=v,
                        latitude_01=row['latitude_01'], 
                        longitude_01=row['longitude_01'],
                        latitude_02=row['latitude_02'], 
                        longitude_02=row['longitude_02'],
                        latitude_03=row['latitude_03'], 
                        longitude_03=row['longitude_03'],
                        p_value=normalized_01_p_value,
                        ethnicity=row['Ethnicity'],
                        mixed_population=row['mixed_population'],
                        geographical_regions=row['geographical_region'],
                        country_participant=row['origin_of_participants'],
                    )
                    vs.save()
                    
                    count += 1
                    if count % 100 == 0:
                        self.stdout.write(f"Processed {count} rows in first import")
                        
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error processing row {index} in first import: {str(e)}"))
                    self.stdout.write(self.style.WARNING(f"Row data: {row}"))
                    continue
            
            self.stdout.write(self.style.SUCCESS("First import job completed successfully"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during first import job: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise

    def process_second_import(self, file_path):
        """Process the second Excel import file"""
        self.stdout.write("Starting second import job...")
        
        try:
            # Import data from the second Excel file
            df_excel = pd.read_excel(file_path)
            self.stdout.write(self.style.SUCCESS(f"Loaded {len(df_excel)} rows from second import file"))
            
            count = 0
            for index, row in df_excel.iterrows():
                try:
                    p01, created = Phenotypeagmp.objects.get_or_create(name=row['phenotype'])
                    s01, created = Studyagmp.objects.get_or_create(
                        data_ac=row['data_ac'], 
                        publication_id=row['PUBMEDID'], 
                        publication_year=row['publication_year'], 
                        study_type=row['study_type'], 
                        title=row['title']
                    )
                    g01, created = Geneagmp.objects.get_or_create(
                        gene_name=row['gene_name'], 
                        gene_id=row['curated_gene_symbol'], 
                        chromosome=row['chromosome'], 
                        uniprot_ac=row['uniprot'], 
                        function=row['function']
                    )
                    v01 = Variantagmp(
                        studyagmp=s01, 
                        phenotypeagmp=p01, 
                        geneagmp=g01, 
                        variant_type=row['variant_type'], 
                        source_db=row['source'], 
                        id_in_source_db=row['id_in_source'], 
                        rs_id=row['id']
                    )
                    v01.save()
                    
                    normalized_p_value = self.normalize_value(row['p-value'])

                    vs01 = VariantStudyagmp(
                        studyagmp=s01, 
                        variantagmp=v01,
                        latitude_01=row['latitude_01'], longitude_01=row['longitude_01'],
                        latitude_02=row['latitude_02'], longitude_02=row['longitude_02'],
                        latitude_03=row['latitude_03'], longitude_03=row['longitude_03'],
                        latitude_04=row['latitude_04'], longitude_04=row['longitude_04'],
                        latitude_05=row['latitude_05'], longitude_05=row['longitude_05'],
                        latitude_06=row['latitude_06'], longitude_06=row['longitude_06'],
                        latitude_07=row['latitude_07'], longitude_07=row['longitude_07'],
                        latitude_08=row['latitude_08'], longitude_08=row['longitude_08'],
                        latitude_09=row['latitude_09'], longitude_09=row['longitude_09'],
                        latitude_10=row['latitude_10'], longitude_10=row['longitude_10'],
                        latitude_11=row['latitude_11'], longitude_11=row['longitude_11'],
                        p_value=normalized_p_value,
                        ethnicity=row['Ethnicity'],
                        mixed_population=row['mixed_population'],
                        geographical_regions=row['geographical_region'],
                        country_participant=row['origin_of_participants'],
                    )
                    vs01.save()
                    
                    count += 1
                    if count % 100 == 0:
                        self.stdout.write(f"Processed {count} rows in second import")
                        
                except Exception as e:
                    self.stdout.write(self.style.WARNING(f"Error processing row {index} in second import: {str(e)}"))
                    self.stdout.write(self.style.WARNING(f"Row data: {row}"))
                    continue
            
            self.stdout.write(self.style.SUCCESS("Second import job completed successfully"))
            
        except Exception as e:
            self.stdout.write(self.style.ERROR(f"Error during second import job: {str(e)}"))
            import traceback
            self.stdout.write(self.style.ERROR(traceback.format_exc()))
            raise

    def print_statistics(self):
        """Print final statistics about imported data"""
        no_of_genes = Geneagmp.objects.values('gene_id').distinct().count()
        no_of_drugs = Drugagmp.objects.values('drug_bank_id').distinct().count()
        no_of_variants = Variantagmp.objects.values('rs_id').distinct().count()
        no_of_studies = Studyagmp.objects.values('publication_id').distinct().count()
        no_of_phenotypes = Phenotypeagmp.objects.values('name').distinct().count()
        no_of_variant_studies = VariantStudyagmp.objects.all().count()

        self.stdout.write("\n")
        self.stdout.write(self.style.SUCCESS(f"{no_of_phenotypes}: TOTAL PHENOTYPES IMPORTED"))
        self.stdout.write(self.style.SUCCESS(f"{no_of_studies}: TOTAL Studies IMPORTED"))
        self.stdout.write(self.style.SUCCESS(f"{no_of_genes}: TOTAL Genes IMPORTED"))
        self.stdout.write(self.style.SUCCESS(f"{no_of_drugs}: TOTAL DRUGS IMPORTED"))
        self.stdout.write(self.style.SUCCESS(f"{no_of_variant_studies}: TOTAL VARIANT STUDIES IMPORTED"))
        self.stdout.write(self.style.SUCCESS(f"{no_of_variants}: TOTAL VARIANTS IMPORTED"))
        self.stdout.write(self.style.SUCCESS("\n############ GWAS Catalogue IMPORT COMPLETE ################"))