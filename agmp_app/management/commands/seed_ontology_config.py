from django.core.management.base import BaseCommand
from agmp_app.models import OntologyConfig, SearchFieldMapping


ONTOLOGIES = [
    ('mondo', 'MONDO Disease Ontology', 'phenotype', 1, True, 1, 30),
    ('doid', 'Disease Ontology', 'phenotype', 2, True, 1, 30),
    ('hp', 'Human Phenotype Ontology', 'phenotype', 3, True, 1, 30),
    ('efo', 'Experimental Factor Ontology', 'phenotype', 4, True, 1, 30),
    ('chebi', 'ChEBI Chemical Entities', 'drug', 1, False, 0, 0),
]

MAPPINGS = [
    ('phenotype', 'phenotypeagmp__name', 'iexact', False),
    ('phenotype', 'phenotypeagmp__name', 'icontains', True),
    ('drug', 'drug_name', 'iexact', False),
    ('drug', 'drug_name', 'icontains', True),
]


class Command(BaseCommand):
    help = 'Seed OntologyConfig and SearchFieldMapping tables'

    def add_arguments(self, parser):
        parser.add_argument(
            '--dry-run',
            action='store_true',
            help='Preview what would be created without making changes',
        )
        parser.add_argument(
            '--reset',
            action='store_true',
            help='Delete existing config before seeding',
        )

    def handle(self, *args, **options):
        dry_run = options['dry_run']
        reset = options['reset']

        if dry_run:
            self.stdout.write(self.style.WARNING('DRY RUN — no changes will be made\n'))

        if reset:
            if dry_run:
                self.stdout.write(f'  Would delete {OntologyConfig.objects.count()} OntologyConfig rows')
                self.stdout.write(f'  Would delete {SearchFieldMapping.objects.count()} SearchFieldMapping rows\n')
            else:
                deleted_onto, _ = OntologyConfig.objects.all().delete()
                deleted_map, _ = SearchFieldMapping.objects.all().delete()
                self.stdout.write(self.style.WARNING(
                    f'  Reset: deleted {deleted_onto} OntologyConfig, {deleted_map} SearchFieldMapping rows\n'
                ))

        self.stdout.write('Ontology sources:')
        for ols_id, name, category, priority, expand, depth, max_children in ONTOLOGIES:
            if dry_run:
                exists = OntologyConfig.objects.filter(ols_id=ols_id).exists()
                status = 'Exists' if exists and not reset else 'Would create'
                self.stdout.write(f'  {status}: {name} ({ols_id}) — {category}')
            else:
                obj, created = OntologyConfig.objects.get_or_create(
                    ols_id=ols_id,
                    defaults={
                        'display_name': name,
                        'category': category,
                        'priority': priority,
                        'expand_children': expand,
                        'child_depth': depth,
                        'max_search_hits': 5,
                        'max_children': max_children,
                    },
                )
                status = 'Created' if created else 'Already exists'
                self.stdout.write(f'  {status}: {obj}')

        self.stdout.write('\nSearch field mappings:')
        for category, field, lookup, fallback in MAPPINGS:
            label = f'{category}: {field}__{lookup}' + (' (fallback)' if fallback else '')
            if dry_run:
                exists = SearchFieldMapping.objects.filter(
                    category=category, lookup_field=field, is_fallback=fallback
                ).exists()
                status = 'Exists' if exists and not reset else 'Would create'
                self.stdout.write(f'  {status}: {label}')
            else:
                obj, created = SearchFieldMapping.objects.get_or_create(
                    category=category,
                    lookup_field=field,
                    lookup_type=lookup,
                    is_fallback=fallback,
                    defaults={'enabled': True},
                )
                status = 'Created' if created else 'Already exists'
                self.stdout.write(f'  {status}: {obj}')

        self.stdout.write(self.style.SUCCESS(
            f'\nDone — OntologyConfig: {OntologyConfig.objects.count()}, '
            f'SearchFieldMapping: {SearchFieldMapping.objects.count()}'
        ))