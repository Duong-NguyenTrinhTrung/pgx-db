# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import PreCachedDrugNetwork

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build PreCachedDrugNetwork Data"

    # source file directory
    drug_atc_data_dir = os.sep.join([settings.DATA_DIR, "json-drug-network"])
    print("drug_atc_data_dir ", drug_atc_data_dir)

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
            self.purge_precached_drug_network_classs()
            self.create_precached_drug_network_class_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_precached_drug_network_classs(self):
        try:
            PreCachedDrugNetwork.objects.all().delete()
        except PreCachedDrugNetwork.DoesNotExist:
            self.logger.warning("PreCachedDrugNetwork mod not found: nothing to delete.")

    def create_precached_drug_network_class_data(self, filenames=False):
        self.logger.info("CREATING PreCachedDrugNetwork")

        atc_codes = [name for name in os.listdir(self.drug_atc_data_dir) if name!=".DS_Store"]
        print("length: ", len(atc_codes))
        for atc_code in atc_codes:
            filenames = os.listdir(self.drug_atc_data_dir+"/"+atc_code)
            try:
                print(atc_code, " ", filenames)
                with open(self.drug_atc_data_dir+"/"+atc_code+"/drug_data.json", "r") as f:
                    drug_data = f.read()
                with open(self.drug_atc_data_dir+"/"+atc_code+"/protein_data.json", "r") as f:
                    protein_data = f.read()
                with open(self.drug_atc_data_dir+"/"+atc_code+"/general_data.json", "r") as f:
                    general_data = f.read()
                with open(self.drug_atc_data_dir+"/"+atc_code+"/interaction_data.json", "r") as f:
                    interaction_data = f.read()
                PreCachedDrugNetwork.objects.create(
                    atc_code=atc_code,
                    drug_json_data=drug_data,
                    protein_json_data=protein_data,
                    general_json_data=general_data,
                    interaction_json_data=interaction_data,
                    )
                # item.save()
            except Exception as e:
                print(e)
            # print("for ", atc_code, " saved. ID: ", item)
