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
                        country_participant_01=row.get('country_01', None),
                        latitude_02=row['latitude_02'], longitude_02=row['longitude_02'],
                        country_participant_02=row.get('country_02', None),
                        latitude_03=row['latitude_03'], longitude_03=row['longitude_03'],
                        country_participant_03=row.get('country_03', None),
                        latitude_04=row['latitude_04'], longitude_04=row['longitude_04'],
                        country_participant_04=row.get('country_04', None),
                        latitude_05=row['latitude_05'], longitude_05=row['longitude_05'],
                        country_participant_05=row.get('country_05', None),
                        latitude_06=row['latitude_06'], longitude_06=row['longitude_06'],
                        country_participant_06=row.get('country_06', None),
                        latitude_07=row['latitude_07'], longitude_07=row['longitude_07'],
                        country_participant_07=row.get('country_07', None),
                        latitude_08=row['latitude_08'], longitude_08=row['longitude_08'],
                        country_participant_08=row.get('country_08', None),
                        latitude_09=row['latitude_09'], longitude_09=row['longitude_09'],
                        country_participant_09=row.get('country_09', None),
                        latitude_10=row['latitude_10'], longitude_10=row['longitude_10'],
                        country_participant_010=row.get('country_10', None),
                        latitude_11=row['latitude_11'], longitude_11=row['longitude_11'],
                        country_participant_011=row.get('country_11', None),
                        latitude_12=row.get('latitude_12', None), longitude_12=row.get('longitude_12', None),
                        country_participant_012=row.get('country_12', None),
                        latitude_13=row.get('latitude_13', None), longitude_13=row.get('longitude_13', None),
                        country_participant_013=row.get('country_13', None),
                        latitude_14=row.get('latitude_14', None), longitude_14=row.get('longitude_14', None),
                        country_participant_014=row.get('country_14', None),
                        latitude_15=row.get('latitude_15', None), longitude_15=row.get('longitude_15', None),
                        country_participant_015=row.get('country_15', None),
                        latitude_16=row.get('latitude_16', None), longitude_16=row.get('longitude_16', None),
                        country_participant_016=row.get('country_16', None),
                        latitude_17=row.get('latitude_17', None), longitude_17=row.get('longitude_17', None),
                        country_participant_017=row.get('country_17', None),
                        latitude_18=row.get('latitude_18', None), longitude_18=row.get('longitude_18', None),
                        country_participant_018=row.get('country_18', None),
                        latitude_19=row.get('latitude_19', None), longitude_19=row.get('longitude_19', None),
                        country_participant_019=row.get('country_19', None),
                        latitude_20=row.get('latitude_20', None), longitude_20=row.get('longitude_20', None),
                        country_participant_20=row.get('country_20', None),
                        latitude_21=row.get('latitude_21', None), longitude_21=row.get('longitude_21', None),
                        country_participant_21=row.get('country_21', None),
                        latitude_22=row.get('latitude_22', None), longitude_22=row.get('longitude_22', None),
                        country_participant_22=row.get('country_22', None),
                        latitude_23=row.get('latitude_23', None), longitude_23=row.get('longitude_23', None),
                        country_participant_23=row.get('country_23', None),
                        latitude_24=row.get('latitude_24', None), longitude_24=row.get('longitude_24', None),
                        country_participant_24=row.get('country_24', None),
                        latitude_25=row.get('latitude_25', None), longitude_25=row.get('longitude_25', None),
                        country_participant_25=row.get('country_25', None),
                        latitude_26=row.get('latitude_26', None), longitude_26=row.get('longitude_26', None),
                        country_participant_26=row.get('country_26', None),
                        latitude_27=row.get('latitude_27', None), longitude_27=row.get('longitude_27', None),
                        country_participant_27=row.get('country_27', None),
                        latitude_28=row.get('latitude_28', None), longitude_28=row.get('longitude_28', None),
                        country_participant_28=row.get('country_28', None),
                        latitude_29=row.get('latitude_29', None), longitude_29=row.get('longitude_29', None),
                        country_participant_29=row.get('country_29', None),
                        latitude_30=row.get('latitude_30', None), longitude_30=row.get('longitude_30', None),
                        country_participant_30=row.get('country_30', None),
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




