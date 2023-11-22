# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import DrugCategory

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build DrugCategory Data"

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
        # print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_drugcategory()
            self.create_drugcategory_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_drugcategory(self):
        try:
            DrugCategory.objects.all().delete()
        except DrugCategory.DoesNotExist:
            self.logger.warning("DrugCategory mod not found: nothing to delete.")

    def create_drugcategory_data(self, filenames=False):
        self.logger.info("CREATING DRUGCATEGORYDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.drugdata_data_dir)
                if fn.endswith("categories.csv")
            ]
            print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.drugdata_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines:
                        values=line[:-1].split(";")
                        drugcategory = values[0]
                        category_detail = values[1][1:-1]


                        c, created = DrugCategory.objects.get_or_create(
                            drugcategory=drugcategory,
                            category_detail=category_detail,
                            )
                        c.save()
                        # print("a record is saved")

        self.logger.info("COMPLETED CREATING DRUGCATEGORY DATA")
