# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import AtcChemicalGroup, AtcPharmacologicalGroup

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build AtcChemicalGroup Data"

    # source file directory
    atc_data_dir = os.sep.join([settings.DATA_DIR, "atc_code"])

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
            self.purge_atc_classs()
            self.create_atc_class_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_atc_classs(self):
        try:
            AtcChemicalGroup.objects.all().delete()
        except AtcChemicalGroup.DoesNotExist:
            self.logger.warning("AtcChemicalGroup mod not found: nothing to delete.")

    def create_atc_class_data(self, filenames=False):
        self.logger.info("CREATING AtcChemicalGroup")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.atc_data_dir)
                # if fn.endswith("ATCcodeCheoupmicalGroup.csv")
                if fn.endswith("ATCcodeChemicalGroup.csv")
            ]
            # print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.atc_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for i, line in enumerate(lines[1:]):
                        # print("row i ", i)
                        values=line[:-1].split(";")
                        id = values[0]
                        name = values[1]
                        parent = values[2]
                        # print("id ", id, "name ", name, "parent ", parent)

                        #fetch data from parent class
                        try:
                            p = AtcPharmacologicalGroup.objects.get(id=parent)
                        except AtcPharmacologicalGroup.DoesNotExist:

                            self.logger.error(
                                "AtcPharmacologicalGroup not found for entry with id {}".format(
                                    parent)
                            )
                            continue

                        c, created = AtcChemicalGroup.objects.get_or_create(
                            id=id,
                            name=name,
                            parent=p
                            )
                        c.save()
                        # print("a record is saved")

        self.logger.info("COMPLETED CREATING AtcChemicalGroup DATA")
