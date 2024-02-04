from drug.models import DrugAtcAssociation, AtcChemicalGroup, AtcPharmacologicalGroup, AtcTherapeuticGroup, AtcChemicalSubstance, AtcAnatomicalGroup
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
            self.calculate_level4(4)
            self.calculate_level3(3)
            self.calculate_level2(2)
            self.calculate_level1(1)
        except Exception as msg:
            print(msg)

    def sub_level_counts(self, level):
        d={}
        with open("Data/genebass_variant_data/Calculation_PGx_variant_rows_per_atc_level"+str(level)+".csv", "r") as f:
            lines = f.readlines()
            for line in lines[1:]:
                values = line[:-1].split(";")
                d[values[0]]=int(values[-1])
        # print(d)
        return d

    def calculate_level4(self, level):
        d = self.sub_level_counts(level+1)
        allChemicalGroupCodes = list(set(AtcChemicalGroup.objects.all().values_list("id", flat=True)))
        with open("Data/genebass_variant_data/Calculation_PGx_variant_rows_per_atc_level"+str(level)+".csv", "w") as f:
            f.write("ATC level"+str(level)+";Drug;Gene;Count\n")
            for i,c in enumerate(allChemicalGroupCodes):
                
                count=0
                #up one level here
                all_sub_codes = list(set(AtcChemicalSubstance.objects.filter(id__istartswith=c).values_list("id", flat=True)))
                print(i, " ", c, " all_sub_codes: ", all_sub_codes)
                for code in all_sub_codes:
                    print("-------- ", code, " ", d.get(code))
                    count+=d.get(code, 0)
                if count>0:
                    print(c," >>>>>>>>>>> total count ", count)
                    f.write(c + ";" +str(count)+"\n")

    def calculate_level3(self, level):
        d = self.sub_level_counts(level+1)
        allPharmacologicalGroupCodes = list(set(AtcPharmacologicalGroup.objects.all().values_list("id", flat=True)))
        with open("Data/genebass_variant_data/Calculation_PGx_variant_rows_per_atc_level"+str(level)+".csv", "w") as f:
            f.write("ATC level"+str(level)+";Drug;Gene;Count\n")
            for i,c in enumerate(allPharmacologicalGroupCodes):
                
                count=0
                #up one level here
                all_sub_codes = list(set(AtcChemicalGroup.objects.filter(id__istartswith=c).values_list("id", flat=True)))
                print(i, " ", c, " all_sub_codes: ", all_sub_codes)
                for code in all_sub_codes:
                    print("-------- ", code, " ", d.get(code))
                    count+=d.get(code, 0)
                if count>0:
                    print(c," >>>>>>>>>>> total count ", count)
                    f.write(c + ";" +str(count)+"\n")


    def calculate_level2(self, level):
        d = self.sub_level_counts(level+1)
        allTherapeuticGroupCodes = list(set(AtcTherapeuticGroup.objects.all().values_list("id", flat=True)))
        with open("Data/genebass_variant_data/Calculation_PGx_variant_rows_per_atc_level"+str(level)+".csv", "w") as f:
            f.write("ATC level"+str(level)+";Drug;Gene;Count\n")
            for i,c in enumerate(allTherapeuticGroupCodes):
                
                count=0
                all_sub_codes = list(set(AtcPharmacologicalGroup.objects.filter(id__istartswith=c).values_list("id", flat=True)))
                print(i, " ", c, " all_sub_codes: ", all_sub_codes)
                for code in all_sub_codes:
                    print("-------- ", code, " ", d.get(code))
                    count+=d.get(code, 0)
                if count>0:
                    print(c," >>>>>>>>>>> total count ", count)
                    f.write(c + ";" +str(count)+"\n")

    def calculate_level1(self, level):
        d = self.sub_level_counts(level+1)
        allAnatomicalGroupCodes = list(set(AtcAnatomicalGroup.objects.all().values_list("id", flat=True)))
        with open("Data/genebass_variant_data/Calculation_PGx_variant_rows_per_atc_level"+str(level)+".csv", "w") as f:
            f.write("ATC level"+str(level)+";Drug;Gene;Count\n")
            for i,c in enumerate(allAnatomicalGroupCodes):
                
                count=0
                all_sub_codes = list(set(AtcTherapeuticGroup.objects.filter(id__istartswith=c).values_list("id", flat=True)))
                print(i, " ", c, " all_sub_codes: ", all_sub_codes)
                for code in all_sub_codes:
                    print("-------- ", code, " ", d.get(code))
                    count+=d.get(code, 0)
                if count>0:
                    print(c," >>>>>>>>>>> total count ", count)
                    f.write(c + ";" +str(count)+"\n")


    