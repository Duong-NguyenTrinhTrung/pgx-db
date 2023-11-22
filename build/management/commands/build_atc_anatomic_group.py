# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import AtcAnatomicalGroup

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build AtcAnatomicalGroup Data"

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
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_atc_classs()
            self.create_atc_class_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_atc_classs(self):
        try:
            AtcAnatomicalGroup.objects.all().delete()
        except AtcAnatomicalGroup.DoesNotExist:
            self.logger.warning("AtcAnatomicalGroup mod not found: nothing to delete.")

    def create_atc_class_data(self, filenames=False):
        self.logger.info("CREATING AtcAnatomicalGroup")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.atc_data_dir)
                if fn.endswith("ATCcodeAnatomicalGroup.csv")
            ]
            print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.atc_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                        values=line[:-1].split(";")
                        id = values[0]
                        name = values[1]


                        c, created = AtcAnatomicalGroup.objects.get_or_create(
                            id=id,
                            name=name,
                            )
                        c.save()
                        print("a record is saved")

        self.logger.info("COMPLETED CREATING ATCcodeAnatomicalGroup DATA")
