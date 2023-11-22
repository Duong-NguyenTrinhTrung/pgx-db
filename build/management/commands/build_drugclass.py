# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import DrugClass

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Drugclass Data"

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
            self.purge_drugclasss()
            self.create_drugclass_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_drugclasss(self):
        try:
            DrugClass.objects.all().delete()
        except DrugClass.DoesNotExist:
            self.logger.warning("Drugclass mod not found: nothing to delete.")

    def create_drugclass_data(self, filenames=False):
        self.logger.info("CREATING DRUGCLASSDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.drugdata_data_dir)
                if fn.endswith("classname.csv")
            ]
            print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.drugdata_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines:
                        values=line[:-1].split(";")
                        drugclass = values[0]
                        class_detail = values[1]


                        c, created = DrugClass.objects.get_or_create(
                            drugclass=drugclass,
                            class_detail=class_detail,
                            )
                        c.save()
                        # print("a record is saved")

        self.logger.info("COMPLETED CREATING DRUGCLASS DATA")
