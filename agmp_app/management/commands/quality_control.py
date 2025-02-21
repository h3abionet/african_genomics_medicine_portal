from django.core.management.base import BaseCommand
from django.db.models import Count
from agmp_app.models import Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, Variantagmp, VariantStudyagmp
import re

class Command(BaseCommand):
    help = 'Find duplicates in the database, validate study types, check for mixed populations, and validate p-values'

    def is_valid_p_value(self, p_value):
        if not p_value or p_value.strip() == '':
            return False
            
        # Remove spaces
        p_value = p_value.strip()
        
        # Return False if p-value is "NR"
        if p_value.upper() == "NR":
            return False
            
        # Check for valid formats:
        # 1. Plain number (e.g., 0.05, .05, 5e-8)
        # 2. Number with < or > (e.g., <0.05, >0.001)
        p_value_pattern = r'^([<>])?\s*(\d*\.?\d+([eE]-?\d+)?|\.?\d+([eE]-?\d+)?)$'
        
        return bool(re.match(p_value_pattern, p_value))

    def handle(self, *args, **kwargs):
        # Define the fields to check for duplicates for each model
        models_to_check = {
            'Drugagmp': ['drug_bank_id', 'drug_name'],
            'Geneagmp': ['gene_id', 'gene_name'],
            'Studyagmp': ['data_ac', 'publication_id'],
            'Phenotypeagmp': ['name'],
            'Variantagmp': ['rs_id', 'variant_type'],
            'VariantStudyagmp': ['variantagmp', 'studyagmp'],
        }

        # Allowed study types
        allowed_study_types = ['Case Report', 'Candidate Gene', 'GWAS', 'WES/WGS', 'Clinical Trial', 'Other']

        # Iterate through each model and check for duplicates
        for model_name, fields in models_to_check.items():
            self.stdout.write(self.style.SUCCESS(f'Checking duplicates for {model_name}...'))
            model = globals()[model_name]
            duplicates = model.objects.values(*fields).annotate(count=Count('id')).filter(count__gt=1)
            
            if duplicates.exists():
                self.stdout.write(self.style.WARNING(f'Duplicates found in {model_name}:'))
                for duplicate in duplicates:
                    self.stdout.write(self.style.ERROR(f'Duplicate fields: {duplicate}'))
                    # Fetch the actual duplicate records
                    duplicate_records = model.objects.filter(**{field: duplicate[field] for field in fields})
                    for record in duplicate_records:
                        self.stdout.write(self.style.ERROR(f' - {record}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'No duplicates found in {model_name}.'))

        # Check for phenotype names containing forward slashes
        self.stdout.write(self.style.SUCCESS('Starting check for phenotype names containing forward slashes...'))
        phenotypes_with_slashes = Phenotypeagmp.objects.filter(name__contains='/')
        if phenotypes_with_slashes.exists():
            self.stdout.write(self.style.WARNING('Found phenotype names containing forward slashes:'))
            for phenotype in phenotypes_with_slashes:
                self.stdout.write(self.style.ERROR(
                    f' - Phenotype ID: {phenotype.id}, '
                    f'Name: {phenotype.name}'
                ))
        else:
            self.stdout.write(self.style.SUCCESS('No phenotype names containing forward slashes found.'))
        self.stdout.write(self.style.SUCCESS('Completed check for phenotype names containing forward slashes.'))

        # Validate study types in Studyagmp model
        self.stdout.write(self.style.SUCCESS('Validating study types in Studyagmp model...'))
        invalid_studies = Studyagmp.objects.exclude(study_type__in=allowed_study_types)
        if invalid_studies.exists():
            self.stdout.write(self.style.WARNING(f'Invalid study types found in Studyagmp:'))
            for study in invalid_studies:
                self.stdout.write(self.style.ERROR(
                    f'Publication ID: {study.publication_id}, '
                    f'Publication Year: {study.publication_year}, '
                    f'Invalid Study Type: {study.study_type}'
                ))
        else:
            self.stdout.write(self.style.SUCCESS('All study types are valid in Studyagmp model.'))

        # Check for mixed populations in VariantStudyagmp model
        self.stdout.write(self.style.SUCCESS('Checking for mixed populations in VariantStudyagmp model...'))
        mixed_population_studies = VariantStudyagmp.objects.filter(mixed_population__in=['TRUE', 'FALSE'])
        if mixed_population_studies.exists():
            self.stdout.write(self.style.WARNING(f'Mixed population studies found in VariantStudyagmp:'))
            for study in mixed_population_studies:
                self.stdout.write(self.style.ERROR(
                    f'Publication ID: {study.studyagmp.publication_id if study.studyagmp else "N/A"}, '
                    f'Mixed Population: {study.mixed_population}'
                ))
        else:
            self.stdout.write(self.style.SUCCESS('No mixed population studies found in VariantStudyagmp model.'))

        # Check for invalid p-values (excluding "NR" values)
        self.stdout.write(self.style.SUCCESS('Checking for invalid p-values in VariantStudyagmp model...'))
        variant_studies = VariantStudyagmp.objects.exclude(p_value__iexact='NR').exclude(p_value__isnull=True).exclude(p_value='')
        invalid_p_values = []
        
        for study in variant_studies:
            if not self.is_valid_p_value(study.p_value):
                invalid_p_values.append({
                    'study_id': study.studyagmp.id if study.studyagmp else "N/A",
                    'publication_id': study.studyagmp.publication_id if study.studyagmp else "N/A",
                    'p_value': study.p_value
                })

        if invalid_p_values:
            self.stdout.write(self.style.WARNING(f'Invalid p-values found in VariantStudyagmp (excluding "NR"):'))
            for invalid in invalid_p_values:
                self.stdout.write(self.style.ERROR(
                    f'Publication ID: {invalid["publication_id"]}, '
                    f'Invalid p-value: {invalid["p_value"]}'
                ))
        else:
            self.stdout.write(self.style.SUCCESS('All p-values are valid in VariantStudyagmp model (excluding "NR").'))

        # Print summary statistics
        self.stdout.write(self.style.SUCCESS('\nSummary Statistics:'))
        
        # Variants count by rs_id (excluding nulls and empty strings)
        variant_count = Variantagmp.objects.exclude(rs_id__isnull=True).exclude(rs_id='').values_list('rs_id', flat=True).distinct().count()
        self.stdout.write(f'* Number of unique values (variant by rs_id): {variant_count}')
        
        # Genes count by gene_id (excluding nulls and empty strings)
        gene_count = Geneagmp.objects.exclude(gene_id__isnull=True).exclude(gene_id='').values_list('gene_id', flat=True).distinct().count()
        self.stdout.write(f'* Number of unique values (gene by gene_id): {gene_count}')
        
        # Drugs count by drug_id (excluding nulls and empty strings)
        drug_count = Drugagmp.objects.exclude(drug_id__isnull=True).exclude(drug_id='').exclude(drug_name__iexact="nan").values_list('drug_id', flat=True).distinct().count()
        self.stdout.write(f'* Number of unique values (drug by drug_id): {drug_count}')
        
        # Phenotypes count by name (excluding nulls and empty strings)
        phenotype_count = Phenotypeagmp.objects.exclude(name__isnull=True).exclude(name='').values('name').distinct().count()
        self.stdout.write(f'* Number of unique values (phenotype by name): {phenotype_count}')
        
        # Studies count by publication_id (excluding nulls and empty strings)
        study_count = Studyagmp.objects.exclude(publication_id__isnull=True).exclude(publication_id='').values_list('publication_id', flat=True).distinct().count()
        self.stdout.write(f'* Number of unique values (study by publication_id): {study_count}')
        
        # Countries count (excluding nulls and empty strings)
        countries = set()
        for field in ['country_participant', 'country_participant_01', 'country_participant_02',
                     'country_participant_03', 'country_participant_04', 'country_participant_05',
                     'country_participant_06', 'country_participant_07', 'country_participant_08',
                     'country_participant_09', 'country_participant_010', 'country_participant_011']:
            values = VariantStudyagmp.objects.exclude(**{f"{field}__isnull": True}).exclude(**{field: ""}).values_list(field, flat=True).distinct()
            countries.update(values)
        self.stdout.write(f'* Number of unique values (country): {len(countries)}')
        
        # Regions count (excluding nulls and empty strings)
        region_count = VariantStudyagmp.objects.exclude(geographical_regions__isnull=True).exclude(geographical_regions='').values_list('geographical_regions', flat=True).distinct().count()
        self.stdout.write(f'* Number of unique values (region): {region_count}')
        
        # Mixed population count (excluding nulls and empty strings)
        mixed_pop_count = VariantStudyagmp.objects.exclude(mixed_population__isnull=True).exclude(mixed_population='').values_list('mixed_population', flat=True).distinct().count()
        self.stdout.write(f'* Number of unique values (mixed population): {mixed_pop_count}')
        
        # Study types count (excluding nulls and empty strings)
        study_type_count = Studyagmp.objects.exclude(study_type__isnull=True).exclude(study_type='').values_list('study_type', flat=True).distinct().count()
        study_types = Studyagmp.objects.exclude(study_type__isnull=True).exclude(study_type='').values_list('study_type', flat=True).distinct()
        self.stdout.write(f'* Number of unique values (study type): {study_type_count}')
        self.stdout.write(f'  Study types: {", ".join(sorted(study_types))}')

        self.stdout.write(self.style.SUCCESS('\nQuality control checks completed.'))