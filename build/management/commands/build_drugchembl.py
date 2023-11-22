# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import DrugChembl

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build DrugChembl Data"

    # source file directory
    drugdata_data_dir = os.sep.join([settings.DATA_DIR, "drug_data"])

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
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_drugchemblclasss()
            self.create_drugchembl_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_drugchemblclasss(self):
        try:
            DrugChembl.objects.all().delete()
        except DrugChembl.DoesNotExist:
            self.logger.warning("DrugCHEMBL mod not found: nothing to delete.")

    def create_drugchembl_data(self, filenames=False):
        self.logger.info("CREATING DRUGCHEMBLDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.drugdata_data_dir)
                if fn.endswith("ChEMBL.csv")
            ]
            print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.drugdata_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines:
                        values=line[:-1].split(";")
                        drugchembl = values[0]
                        chembl_detail = values[1]


                        s, created = DrugChembl.objects.get_or_create(
                            drugchembl=drugchembl,
                            chembl_detail=chembl_detail,
                            )
                        s.save()
                        # print("a record is saved")

        self.logger.info("COMPLETED CREATING DRUGCHEMBL DATA")
