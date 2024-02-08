# build_interaction.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from drug.models import Drug
from gene.models import Gene
from variant.models import Pharmgkb

from optparse import make_option
import logging
import csv
import os
import pandas as pd
import numpy as np


class Command(BaseCommand):
    help = "Build interaction Data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    pharmgkbdata_data_dir = os.sep.join(
        [str(settings.DATA_DIR), "pharmgkb_data"])

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_pharmgkb()
            self.create_pharmgkb_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_pharmgkb(self):
        print("checkpoint 1.2 inside purge_pharmgkb function ")
        try:
            Pharmgkb.objects.all().delete()
        except Pharmgkb.DoesNotExist:
            self.logger.warning(
                "Pharmgkb mod not found: nothing to delete.")

    def convert(self, s):
        # print(s, " ", type(s))
        if not (isinstance(s, float)):
            sign = s.split()[0]
            if sign=="=":
                return float(s.split()[1])
            else:
                if sign==">":
                    return float(s.split()[1]) + 0.00001
                else:
                    return float(s.split()[1]) - 0.00001
        else:
            return None
        
        

    def create_pharmgkb_data(self, filenames=False):
        print("checkpoint 1.4 start of create_pharmgkb_data function ")
        self.logger.info("CREATING PHARMGKB")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.pharmgkbdata_data_dir)
                if fn.endswith("pharmgkb_variant_data.csv")
            ]
            print("checkpoint2")
            print(filenames)

        for filename in filenames:

            filepath = os.sep.join([self.pharmgkbdata_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep=";")

            print("data length = ", len(data))
            print("data column = ", data.columns)
            for index, row in enumerate(data.iterrows()):
                #;Variant_Annotation_ID;Variant_or_Haplotypes;PMID;Phenotype_Category;Significance;Notes;Sentence;Alleles;P_Value;Biogeographical_Groups;Study_Type;Study_Cases;Study_Controls;Direction_of_effect;PD_PK_terms;Metabolizer_types;drugbank_id;drugname;genename;geneid


                VariantAnnotationID = data[index: index + 1]["Variant_Annotation_ID"].values[0]
                Variant_or_Haplotypes = data[index: index + 1]["Variant_or_Haplotypes"].values[0]
                pmid = data[index: index + 1]["PMID"].values[0] 
                Phenotype_Category = data[index: index + 1]["Phenotype_Category"].values[0]
                Significance = data[index: index + 1]["Significance"].values[0]
                Notes = data[index: index + 1]["Notes"].values[0] 
                Sentence = data[index: index + 1]["Sentence"].values[0] 
                Alleles = data[index: index + 1]["Alleles"].values[0]
                P_Value = data[index: index + 1]["P_Value"].values[0]
                P_Value_numeric = self.convert(data[index: index + 1]["P_Value"].values[0])
                Biogeographical_Groups = data[index: index + 1]["Biogeographical_Groups"].values[0]
                Study_Type = data[index: index + 1]["Study_Type"].values[0]
                Study_Cases = data[index: index + 1]["Study_Cases"].values[0]
                Study_Controls = data[index: index + 1]["Study_Controls"].values[0]
                Direction_of_effect = data[index: index + 1]["Direction_of_effect"].values[0]
                PD_PK_terms = data[index: index + 1]["PD_PK_terms"].values[0]
                Metabolizer_types = data[index: index + 1]["Metabolizer_types"].values[0]
                drugbank_id = data[index: index + 1]["drugbank_id"].values[0] 
                gene_id = data[index: index + 1]["geneid"].values[0] 

                # fetch drug

                try:
                    d = Drug.objects.get(drug_bankID=drugbank_id)
                except Drug.DoesNotExist:

                    self.logger.error(
                        "Drug not found for entry with drugbank ID {}".format(
                            drugbank_id)
                    )
                    continue

                # fetch gene data
                try:
                    g = Gene.objects.get(gene_id=gene_id)
                except Gene.DoesNotExist:

                    self.logger.error(
                        "Gene not found for entry with gene ID {}".format(
                            gene_id)
                    )
                    continue

                # print("checkpoint 2.1 - start to fetch data to interaction table")
                interaction, created = Pharmgkb.objects.get_or_create(
                    VariantAnnotationID = VariantAnnotationID,
                    Variant_or_Haplotypes = Variant_or_Haplotypes,
                    PMID = pmid ,
                    Phenotype_Category = Phenotype_Category,
                    Significance = Significance,
                    Notes = Notes ,
                    Sentence = Sentence ,
                    Alleles = Alleles,
                    P_Value = P_Value,
                    P_Value_numeric = P_Value_numeric,
                    Biogeographical_Groups = Biogeographical_Groups,
                    Study_Type = Study_Type,
                    Study_Cases = Study_Cases,
                    Study_Controls = Study_Controls,
                    Direction_of_effect = Direction_of_effect,
                    PD_PK_terms = PD_PK_terms,
                    Metabolizer_types = Metabolizer_types,
                    drugbank_id = d,
                    geneid = g,
                )
                interaction.save()
                # print("a record is saved")

        self.logger.info("COMPLETED CREATING PHARMGKB")
