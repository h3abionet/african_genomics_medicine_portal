
import csv
from django.core.management.base import BaseCommand

from agmp_app.models import drug


SILENT, NORMAL, VERBOSE, VERY_VERBOSE = 0, 1, 2, 3

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

        with open(file_path) as f:
            reader = csv.reader(f)
            for rownum, (drug_id, drug_name, drug_bank_id, state, indication, iupac_name) in \
            enumerate(reader):
                if rownum == 0:
                    # let's skip the column captions
                    continue
                drugs, created = \
                drug.objects.get_or_create(
                    id=drug_id,
                    drug_name=drug_name,
                    drug_bank_id=drug_bank_id,
                    state=state,
                    indication=indication,
                    iupac_name=iupac_name,
                )
                if verbosity >= NORMAL:
                    self.stdout.write("{}. {}".format(
                        rownum, drug.drug_name
                    ))