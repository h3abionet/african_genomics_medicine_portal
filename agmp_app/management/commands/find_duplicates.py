from django.core.management.base import BaseCommand
from django.db.models import Count
from django.apps import apps
from django.db import models
import json
from datetime import datetime
from typing import List, Dict, Any, Type


class DuplicateChecker:
    def __init__(self, model: Type[models.Model]):
        self.model = model
        self.fields = self._get_checkable_fields()
        
    def _get_checkable_fields(self) -> List[str]:
        """Get specific fields to check for duplicates."""
        allowed_fields = {
            'drug_id', 'drug_bank_id', 'drug_name',
            'gene_id', 'gene_name', 'publication_id', 'rs_id'
        }
        model_fields = {field.name for field in self.model._meta.fields}
        return list(allowed_fields & model_fields)
    
    def find_duplicates(self, min_count: int = 2) -> Dict[str, List[Dict[str, Any]]]:
        """Find duplicate records using specified fields."""
        results = {}
        for field in self.fields:
            duplicates = (
                self.model.objects
                .values(field)
                .annotate(count=Count('id'))
                .filter(count__gte=min_count)
                .order_by('-count')
            )
            
            if duplicates:
                results[field] = []
                
                for dup in duplicates:
                    # Get all records matching these field values
                    filters = {field: dup[field]}
                    records = self.model.objects.filter(**filters)
                    
                    # Collect detailed information about each duplicate record
                    record_info = []
                    for record in records:
                        info = {'id': record.id, 'str_representation': str(record)}
                        for f in self.fields:
                            value = getattr(record, f, None)
                            info[f] = str(value) if value is not None else None
                        record_info.append(info)
                    
                    results[field].append({
                        'matching_value': dup[field],
                        'count': dup['count'],
                        'records': record_info
                    })
        
        return results


class Command(BaseCommand):
    help = 'Find duplicate records in specific fields across all models'

    def add_arguments(self, parser):
        parser.add_argument(
            '--model',
            type=str,
            help='Specific model to check (e.g., app_label.ModelName)'
        )
        parser.add_argument(
            '--min-count',
            type=int,
            default=2,
            help='Minimum number of duplicates to report (default: 2)'
        )
        parser.add_argument(
            '--output',
            type=str,
            help='Output file path for detailed JSON report'
        )

    def handle(self, *args, **options):
        app_models = apps.get_models()
        specified_model = options['model']
        min_count = options['min_count']
        output_file = options['output']
        complete_results = {}

        if specified_model:
            try:
                app_label, model_name = specified_model.split('.')
                model = apps.get_model(app_label, model_name)
                app_models = [model]
            except (ValueError, LookupError):
                self.stdout.write(self.style.ERROR(f"Invalid model: {specified_model}"))
                return

        for model in app_models:
            model_name = f"{model._meta.app_label}.{model._meta.model_name}"
            self.stdout.write(self.style.SUCCESS(f"\nChecking {model_name} for duplicates..."))
            
            checker = DuplicateChecker(model)
            duplicates = checker.find_duplicates(min_count=min_count)
            
            if not duplicates:
                self.stdout.write(self.style.SUCCESS(f"No duplicates found in {model_name}"))
                continue

            complete_results[model_name] = duplicates
            for field, duplicate_sets in duplicates.items():
                self.stdout.write(self.style.WARNING(f"\nFound duplicates based on field: {field}"))
                self.stdout.write(f"Number of duplicate sets: {len(duplicate_sets)}")
                for dup_set in duplicate_sets:
                    self.stdout.write(f"Matching value: {dup_set['matching_value']}")
                    self.stdout.write(f"Number of duplicates: {dup_set['count']}")

        if output_file:
            timestamp = datetime.now().strftime('%Y%m%d_%H%M%S')
            output_path = f"{output_file}_{timestamp}.json"
            with open(output_path, 'w') as f:
                json.dump(complete_results, f, indent=2)
            self.stdout.write(self.style.SUCCESS(f"\nDetailed results saved to {output_path}"))
