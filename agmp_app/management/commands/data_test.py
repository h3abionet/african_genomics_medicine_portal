#!/usr/bin/env python

from agmp_app.models import Gene, Variant, Drug
from os import path
from django.core.management.base import BaseCommand, CommandError
import pandas as pd
from django.db.models import Q
from django_pandas.io import read_frame


def genes_table_test(gene_file):
    """TODO: Docstring for genes.

    :arg1: TODO
    :returns: TODO

    """
    try:
        data = pd.read_csv(
            gene_file,
            usecols=["gene_id", "chromosome",
                     "gene_name", "uniprot_ac", "function"],
        )
        gene_id_dup = data.groupby("gene_id").size().reset_index()
        gene_id_dup = gene_id_dup[gene_id_dup[0] > 1]
        if len(gene_id_dup):
            dup_genes = ", ".join(gene_id_dup["gene_id"].values)
            exit(f"{dup_genes} have duplicated values. exiting . . . .")

        gene_name_dup = data.groupby("gene_name").size().reset_index()
        gene_name_dup = gene_name_dup[gene_name_dup[0] > 1]
        if len(gene_name_dup):
            dup_genes = ", ".join(gene_name_dup["gene_name"].values)
            exit(f"{dup_genes} have duplicated values. exiting . . . .")

        # NOTE: Check the existance in the data base itself
        for _, row in data.iterrows():
            qry = Q(gene_id__exact=row["gene_id"]) | Q(
                gene_name__exact=row["gene_name"])
            genes_already_in_repo = read_frame(Gene.objects.filter(qry))
            genes_already_in_repo = genes_already_in_repo[
                ~((genes_already_in_repo["gene_id"] == row["gene_id"]) &
                  (genes_already_in_repo["gene_name"] == row["gene_name"]))
            ]
            if len(genes_already_in_repo):
                print(
                    f"Please check for [{row['gene_id']}, {row['gene_name']}]. They have have addition exiting values in repo table")

    except:
        exit(
            f"One or more columns among gene_id, chromosome, gene_name, uniprot_ac, function are missing {gene_file}"
        )


class Command(BaseCommand):
    help = "Closes the specified poll for voting"

    def add_arguments(self, parser):
        # parser.add_argument('genes_file','--genes_file', type=str)
        parser.add_argument(
            "--genes",
            action="store",
            dest="genes_file",
            type=str,
            help="csv file containing the genes",
        )
        parser.add_argument(
            "--drugs",
            action="store",
            dest="drugs_file",
            type=str,
            help="csv file containing the drugs",
        )
        parser.add_argument(
            "--variants",
            action="store",
            dest="variants_file",
            type=str,
            help="csv file containing the variants",
        )
        parser.add_argument(
            "--keep",
            action="store_true",
            dest="keep_entities",
            default=False,
            help="Keeps existing entities before loading",
        )

    def handle(self, *args, **options):
        if not options["keep_entities"]:
            print(f"Deleting existing entities first...", end="")
            Gene.objects.all().delete()
            Variant.objects.all().delete()
            Drug.objects.all().delete()
            print(f"done.")

        # ingest Drugs
        drugs_file = options["drugs_file"]
        variants_file = options["variants"]
        gene_fike = options["genes"]
        if not drugs_file:
            print("Drug file not provided. Skipping testing")
        if not path.isfile(drugs_file):
            print(
                f"Given file {drugs_file} is not a file for doesn't exits. ignoring update."
            )
