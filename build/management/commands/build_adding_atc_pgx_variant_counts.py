# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import DrugAtcAssociation, Drug, AtcChemicalSubstance
from variant.models import GenebassVariantPGx

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):

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

        try:
            self.adding_atc_level_pgx_variant_count()
        except Exception as msg:
            print(msg)
            self.logger.error(msg)


    def adding_atc_level_pgx_variant_count(self, filenames=False):
        
        atcs = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        with open("atc_variant_based_pgx_count.csv", "w") as f:
            f.write("ATC code,drug,count\n")
            for atc in atcs:
                drug_list = DrugAtcAssociation.objects.filter(atc_id=atc).values_list("drug_id", flat=True)
                count=0
                for drug in drug_list:
                    items = GenebassVariantPGx.objects.filter(drugbank_id__drug_bankID=drug)
                    count+=len(items)
                    if len(items)>0:
                        print("count = ", len(items), " for drug ", drug)
                        f.write(atc+","+drug+","+str(len(items))+",\n")
                if count>0: 
                    print("count = ", count, " for atc code ", atc)





