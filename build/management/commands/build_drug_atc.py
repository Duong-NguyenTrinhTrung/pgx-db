# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import DrugAtcAssociation, Drug, AtcChemicalSubstance

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build DrugAtcAssociation Data"

    # source file directory
    drug_atc_data_dir = os.sep.join([settings.DATA_DIR, "drug_atc"])

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
            self.purge_drug_atc_classs()
            self.create_drug_atc_class_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_drug_atc_classs(self):
        try:
            DrugAtcAssociation.objects.all().delete()
        except DrugAtcAssociation.DoesNotExist:
            self.logger.warning("DrugAtcAssociation mod not found: nothing to delete.")

    def create_drug_atc_class_data(self, filenames=False):
        self.logger.info("CREATING DrugAtcAssociation")

        atc_missing=[]
        drug_missing=[]

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.drug_atc_data_dir)
                if fn.endswith("drug_atc.csv")
            ]
            print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.drug_atc_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines:
                        values=line[:-1].split(";")
                        drug_id = values[1]
                        atc_id = values[2]

                        #fetch data from parent drug class
                        try:
                            d = Drug.objects.get(drug_bankID=drug_id)
                        except Drug.DoesNotExist:

                            drug_missing.append(drug_id)
                            

                            self.logger.error(
                                "Drug not found for entry with drug_bankID {}".format(
                                    drug_id)
                            )
                            continue

                        #fetch data from parent chemical substance class
                        try:
                            c = AtcChemicalSubstance.objects.get(id=atc_id)
                        except AtcChemicalSubstance.DoesNotExist:
                            atc_missing.append(atc_id)

                            self.logger.error(
                                "AtcChemicalSubstance not found for entry with id {}".format(
                                    atc_id)
                            )
                            continue


                        r, created = DrugAtcAssociation.objects.get_or_create(
                            drug_id=d,
                            atc_id=c,
                            )
                        r.save()
                        # print("a record is saved")
        print("\n\n----------- atc_missing : ",atc_missing)
        print("\n\n----------- len atc_missing : ",len(atc_missing))
        print("\n\n----------- drug_missing : ",drug_missing)
        print("\n\n----------- len drug_missing : ",len(drug_missing))

        self.logger.info("COMPLETED CREATING ATCcodeAnatomicalGroup DATA")
