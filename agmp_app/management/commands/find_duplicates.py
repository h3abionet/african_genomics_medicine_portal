from django.core.management.base import BaseCommand
from django.db.models import Count
from agmp_app.models import Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, Variantagmp, VariantStudyagmp

class Command(BaseCommand):
    help = 'Find duplicates in the database based on specified fields'

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

        self.stdout.write(self.style.SUCCESS('Duplicate check completed.'))