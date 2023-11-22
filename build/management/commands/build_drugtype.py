# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import DrugType

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Drugtype Data"

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
            self.purge_drugtypes()
            self.create_drugtype_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_drugtypes(self):
        print("checkpoint 1.2 inside purge_drugtypes function ")
        try:
            DrugType.objects.all().delete()
        except DrugType.DoesNotExist:
            self.logger.warning("Drugtypes mod not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_drugtypes function ")

   

    def create_drugtype_data(self, filenames=False):
        self.logger.info("CREATING DRUGTYPEDATA")

        # print("checkpoint start to fetch data to Drugtype table")
        type, created = DrugType.objects.get_or_create(
            drugtype=0,
            type_detail="Biotech",
            )
        type.save()
        print("a record is saved")

        type, created = DrugType.objects.get_or_create(
            drugtype=1,
            type_detail="Small Molecule",
            )
        type.save()
        print("a record is saved")


        self.logger.info("COMPLETED CREATING DRUGTYPE DATA")
