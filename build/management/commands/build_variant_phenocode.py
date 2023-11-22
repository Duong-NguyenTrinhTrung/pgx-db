# build_genebass_variant.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from variant.models import VariantPhenocode


from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Variant Phenocode Data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    variantphenocodedata_data_dir = os.sep.join(
        [settings.DATA_DIR, "variantphenocode_data"])

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_phenocode()
            self.create_phenocode_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_phenocode(self):
        print("checkpoint 1.2 inside purge_phenocode function ")
        try:
            VariantPhenocode.objects.all().delete()
        except VariantPhenocode.DoesNotExist:
            self.logger.warning(
                "VariantPhenocode mod not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_variant_phenocode function ")

    def create_phenocode_data(self, filenames=False):
        print("checkpoint 1.4 ")
        self.logger.info("CREATING VARIANT PHENOCODE DATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.variantphenocodedata_data_dir)
                if fn.endswith("phenocode_data.csv")
            ]
            print("checkpoint2")
            print(filenames)

        for filename in filenames:

            filepath = os.sep.join(
                [self.variantphenocodedata_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1")

            print("data length = ", len(data))
            print("data column = ", data.columns)
            for index, row in enumerate(data.iterrows()):
                phenocode = data[index: index + 1]["phenocode"].values[0]
                description = data[index: index + 1]["description"].values[0]
                description_more = data[index: index +
                                        1]["description_more"].values[0]
                pheno_sex = data[index: index +
                                        1]["pheno_sex"].values[0]

                # print(
                #     "checkpoint 2.1 - start to fetch data to genebass variant table")

                ph, created = VariantPhenocode.objects.get_or_create(
                    phenocode=phenocode,
                    description=description,
                    description_more=description_more,
                    pheno_sex=pheno_sex
                )
                print("checkpoint")
                ph.save()
                print("a record is saved")

        self.logger.info("COMPLETED CREATING VARIANT PHENOCODE DATA")
