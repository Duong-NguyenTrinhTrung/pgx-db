# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import DrugGroup

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Druggroup Data"

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
            self.purge_druggroups()
            self.create_druggroup_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_druggroups(self):
        try:
            DrugGroup.objects.all().delete()
        except DrugGroup.DoesNotExist:
            self.logger.warning("Drugnames mod not found: nothing to delete.")

    def create_druggroup_data(self, filenames=False):
        self.logger.info("CREATING DRUGGROUPDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.drugdata_data_dir)
                if fn.endswith("groups.csv")
            ]
            print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.drugdata_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines:
                        values=line[:-1].split(";")
                        druggroup = values[0]
                        group_detail = values[1][1:-1]


                        group, created = DrugGroup.objects.get_or_create(
                            druggroup=druggroup,
                            group_detail=group_detail,
                            )
                        group.save()
                        # print("a record is saved")

        self.logger.info("COMPLETED CREATING DRUGGROUP DATA")
