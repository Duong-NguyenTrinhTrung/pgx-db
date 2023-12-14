# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import Drug
from gene.models import Gene
from variant.models import GenebassPGx, VariantPhenocode

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build genebass pgx data"

    # source file directory
    gb_pgx_data_dir = os.sep.join([settings.DATA_DIR, "genebass_variant_data"])

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )
    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        # print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_gb_pgx_classs()
            self.create_gb_pgx_class_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_gb_pgx_classs(self):
        try:
            GenebassPGx.objects.all().delete()
        except GenebassPGx.DoesNotExist:
            self.logger.warning("GenebassPGx mod not found: nothing to delete.")

    def create_gb_pgx_class_data(self, filenames=False):
        self.logger.info("CREATING GenebassPGx")


        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.gb_pgx_data_dir)
                if fn.endswith("PGx_data_from_genebass.csv")
            ]
            print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.gb_pgx_data_dir, filename])
            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep=";")

            for index, row in enumerate(data.iterrows()):
                gene_id = data[index: index + 1]["gene_id"].values[0]
                n_cases = data[index: index + 1]["n_cases"].values[0]
                n_controls = data[index: index + 1]["n_controls"].values[0]
                phenocode = data[index: index + 1]["phenocode"].values[0]
                coding_description = data[index: index + 1]["coding_description"].values[0]
                Pvalue = data[index: index + 1]["Pvalue"].values[0]
                Pvalue_Burden = data[index: index + 1]["Pvalue_Burden"].values[0]
                Pvalue_SKAT = data[index: index + 1]["Pvalue_SKAT"].values[0]
                BETA_Burden = data[index: index + 1]["BETA_Burden"].values[0]
                SE_Burden = data[index: index + 1]["SE_Burden"].values[0]
                drugbank_id = data[index: index + 1]["drugbank_id"].values[0]

                # fetch gene
                try:
                    g = Gene.objects.get(gene_id=gene_id)
                except Gene.DoesNotExist:

                    self.logger.error(
                        "Gene not found for gene id {}".format(
                            gene_id)
                    )
                    continue

                # fetch variant phenocode
                try:
                    p = VariantPhenocode.objects.get(phenocode=phenocode)
                except VariantPhenocode.DoesNotExist:

                    self.logger.error(
                        "VariantPhenocode not found for phenocode {}".format(
                            phenocode)
                    )
                    continue

                # fetch drug
                try:
                    d = Drug.objects.get(drug_bankID=drugbank_id)
                except Drug.DoesNotExist:

                    self.logger.error(
                        "Drug not found for drug_bankID {}".format(
                            drugbank_id)
                    )
                    continue

                pgx, created = GenebassPGx.objects.get_or_create(
                    gene_id = g,
                    n_cases = n_cases,
                    n_controls = n_controls,
                    phenocode = p,
                    coding_description = coding_description,
                    Pvalue = Pvalue,
                    Pvalue_Burden = Pvalue_Burden,
                    Pvalue_SKAT = Pvalue_SKAT,
                    BETA_Burden = BETA_Burden,
                    SE_Burden = SE_Burden,
                    drugbank_id = d,
                )

                pgx.save()