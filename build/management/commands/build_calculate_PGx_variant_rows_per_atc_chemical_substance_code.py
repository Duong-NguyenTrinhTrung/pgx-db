from drug.models import DrugAtcAssociation
from variant.models import GenebassVariantPGx
from interaction.models import Interaction
from drug.models import Drug

from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
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
            help="",
        )

    def handle(self, *args, **options):

        try:
            self.calculate()
        except Exception as msg:
            print(msg)

    def calculate(self):
        allChemicalSubstanceCodes = list(set(DrugAtcAssociation.objects.all().values_list("atc_id_id", flat=True)))
        with open("Data/genebass_variant_data/Calculation_PGx_variant_rows_per_atc_level5.csv", "w") as f:
            f.write("ATC level5;Drug;Gene;Count\n")
            for i,c in enumerate(allChemicalSubstanceCodes):
                # print(i, " ", c)
                drugs = list(set(DrugAtcAssociation.objects.filter(atc_id=c).select_related('drug_id').values_list("drug_id", flat=True)))
                drug_objs = Drug.objects.filter(drug_bankID__in=drugs)
                gene_names = list(set(Interaction.objects.filter(drug_bankID__in=drugs).values_list("uniprot_ID__genename", flat=True)))
                
                count=0
                for drug in drug_objs:
                    genebass_data = GenebassVariantPGx.objects.filter(drugbank_id=drug, genename__in=gene_names)
                    count+=genebass_data.count()
                # print(i, " ", c, " ", drugs," ", gene_names, " ", count)
                if count>0:
                    print(i, " ", c, " ", drugs," ", gene_names, " ", count)
                    f.write(c + ";" + ",".join(drugs) + ";" + ",".join(gene_names) + ";"+str(count)+"\n")
