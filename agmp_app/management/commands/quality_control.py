from django.core.management.base import BaseCommand
from django.db.models import Count
from agmp_app.models import Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, Variantagmp, VariantStudyagmp

class Command(BaseCommand):
    help = 'Find duplicates in the database, validate study types, and check for mixed populations'

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
                        self.stdout.write(self.style.ERROR(f'  - {record}'))
            else:
                self.stdout.write(self.style.SUCCESS(f'No duplicates found in {model_name}.'))

        # Validate study types in Studyagmp model
        self.stdout.write(self.style.SUCCESS('Validating study types in Studyagmp model...'))
        invalid_studies = Studyagmp.objects.exclude(study_type__in=allowed_study_types)
        if invalid_studies.exists():
            self.stdout.write(self.style.WARNING(f'Invalid study types found in Studyagmp:'))
            for study in invalid_studies:
                self.stdout.write(self.style.ERROR(
                    f'  - Study ID: {study.id}, '
                    f'Publication ID: {study.publication_id}, '
                    f'Publication Year: {study.publication_year}, '
                    # f'Publication Title: {study.title}, '
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
                    f'  - Variant Study ID: {study.id}, '
                    f'Variant ID: {study.variantagmp.id if study.variantagmp else "N/A"}, '
                    f'Study ID: {study.studyagmp.id if study.studyagmp else "N/A"}, '
                    f'Mixed Population: {study.mixed_population}'
                ))
        else:
            self.stdout.write(self.style.SUCCESS('No mixed population studies found in VariantStudyagmp model.'))

        self.stdout.write(self.style.SUCCESS('Quality control checks completed.'))