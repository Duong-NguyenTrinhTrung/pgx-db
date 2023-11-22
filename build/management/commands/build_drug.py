# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import Drug, DrugCategory, DrugClass, DrugGroup, DrugParent, DrugPubChemCompound, DrugSubclass, DrugSuperclass, DrugType, DrugChembl, DrugPubChemSubstance

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Drug Data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    drugdata_data_dir = os.sep.join([settings.DATA_DIR, "drug_data"])

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_drugs()
            self.create_drug_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_drugs(self):
        print("checkpoint 1.2 inside purge_drugs function ")
        try:
            Drug.objects.all().delete()
        except Drug.DoesNotExist:
            self.logger.warning("Drugs mod not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_drugs function ")

    def create_drug_data(self, filenames=False):
        print("checkpoint 1.4 start of create_drug_data function ")
        self.logger.info("CREATING DRUGDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.drugdata_data_dir)
                if fn.endswith("drug_data.csv")
            ]
            print("checkpoint2")
            print(filenames)

        #predecated
        #process drug encoded data - to reduce data, some columns are encoded and this is for decoded
        # col_map = {"0":"drugtype",
        #             "1":"name",
        #             "2":"superclass",
        #             "3":"classname",
        #             "4":"subclass",
        #             "5":"direct_parent",
        #             "6":"groups",
        #             "7":"categories",
        #             "8":"pubChemCompound",
        #             "9":"interaction_type"
        #             }
            
            
        #read the drug data
        for filename in filenames:

            filepath = os.sep.join([self.drugdata_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep=";")

            # print("checkpoint 2.1 - start to fetch data to Drug table")

            for index, row in enumerate(data.iterrows()):

                drug_bankID = data[index: index + 1]["drugbank_id"].values[0]
                drugtype = data[index: index + 1]["drugtype"].values[0]
                drugname = data[index: index + 1]["name"].values[0]
                druggroup = data[index: index + 1]["groups"].values[0]
                drugcategory = data[index: index + 1]["categories"].values[0]
                drugsuperclass = data[index: index + 1]["superclass"].values[0]
                drugclass = data[index: index + 1]["classname"].values[0]
                drugsubclass = data[index: index + 1]["subclass"].values[0]
                drugparent = data[index: index +
                                     1]["direct_parent"].values[0]
                drugcompound = data[index: index + 1]["PubChemCompound"].values[0] 
                description = data[index: index + 1]["description"].values[0]
                aliases = data[index: index + 1]["aliases"].values[0]
                indication = data[index: index + 1]["indication"].values[0]
                pharmacodynamics = data[index: index +
                                        1]["pharmacodynamics"].values[0]
                moa = data[index: index + 1]["moa"].values[0]
                absorption = data[index: index + 1]["absorption"].values[0]
                toxicity = data[index: index + 1]["toxicity"].values[0]
                halflife = data[index: index + 1]["halflife"].values[0]
                distribution_volume = data[index: index +
                                           1]["distribution_volume"].values[0]
                protein_binding = data[index: index +
                                       1]["protein_binding"].values[0]
                dosages = data[index: index + 1]["dosages"].values[0]
                properties = data[index: index + 1]["properties"].values[0]

                chEMBL = data[index: index + 1]["ChEMBL"].values[0] 
                pubChemSubstance = data[index: index + 1]["PubChemSubstance_ID"].values[0] 
                
                # fetch drugtype
                try:
                    print("i am here")
                    drugtype = DrugType.objects.get(drugtype=drugtype)
                except DrugType.DoesNotExist:

                    self.logger.error(
                        "DrugType not found for drugtype {}".format(
                            drugtype)
                    )
                    continue

               
                # fetch druggroup
                try:
                    druggroup = DrugGroup.objects.get(druggroup=druggroup)
                except DrugGroup.DoesNotExist:

                    self.logger.error(
                        "DrugGroup not found for druggroup {}".format(
                            druggroup)
                    )
                    continue

                # fetch drugclass
                try:
                    drugclass = DrugClass.objects.get(drugclass=drugclass)
                except DrugClass.DoesNotExist:

                    self.logger.error(
                        "DrugClass not found for drugclass {}".format(
                            drugclass)
                    )
                    continue

                # fetch drugsubclass
                try:
                    drugsubclass = DrugSubclass.objects.get(drugsubclass=drugsubclass)
                except DrugSubclass.DoesNotExist:

                    self.logger.error(
                        "DrugSubclass not found for drugsubclass {}".format(
                            drugsubclass)
                    )
                    continue

                # fetch drugsuperclass
                try:
                    drugsuperclass = DrugSuperclass.objects.get(drugsuperclass=drugsuperclass)
                except DrugSuperclass.DoesNotExist:

                    self.logger.error(
                        "DrugSuperclass not found for drugsuperclass {}".format(
                            drugsuperclass)
                    )
                    continue

                # fetch drugparent
                try:
                    drugparent = DrugParent.objects.get(drugparent=drugparent)
                except DrugParent.DoesNotExist:

                    self.logger.error(
                        "DrugParent not found for drugparent {}".format(
                            drugparent)
                    )
                    continue

                # fetch drugcategory
                try:
                    drugcategory = DrugCategory.objects.get(drugcategory=drugcategory)
                except DrugCategory.DoesNotExist:

                    self.logger.error(
                        "DrugCategory not found for drugcategory {}".format(
                            drugcategory)
                    )
                    continue

                # fetch drugcompound
                try:
                    drugcompound = DrugPubChemCompound.objects.get(compound=drugcompound)
                except DrugPubChemCompound.DoesNotExist:

                    self.logger.error(
                        "DrugPubChemCompound not found for drugcompound {}".format(
                            drugcompound)
                    )
                    continue

                # fetch DrugPubChemSubstance
                try:
                    pubChemSubstance = DrugPubChemSubstance.objects.get(drugpubchemblsubstance=pubChemSubstance)
                except DrugPubChemSubstance.DoesNotExist:
                        
                    self.logger.error(
                            "DrugPubChemSubstance not found for DrugPubChemSubstance {}".format(
                                pubChemSubstance)
                        )
                    continue

                # fetch DrugChembl
                try:
                    chEMBL = DrugChembl.objects.get(drugchembl=chEMBL)
                except DrugChembl.DoesNotExist:
                            
                    self.logger.error(
                            "DrugChembl not found for DrugChembl {}".format(
                                chEMBL)
                        )
                    continue

                drug, created = Drug.objects.get_or_create(
                    drug_bankID=drug_bankID,
                    drugtype=drugtype,
                    name=drugname,
                    groups=druggroup,
                    categories=drugcategory,
                    description=description,
                    aliases=aliases,
                    superclass=drugsuperclass,
                    classname=drugclass,
                    subclass=drugsubclass,
                    direct_parent=drugparent,
                    indication=indication,
                    pharmacodynamics=pharmacodynamics,
                    moa=moa,
                    absorption=absorption,
                    toxicity=toxicity,
                    halflife=halflife,
                    distribution_volume=distribution_volume,
                    protein_binding=protein_binding,
                    dosages=dosages,
                    properties=properties,
                    chEMBL = chEMBL, 
                    pubChemCompound = drugcompound, 
                    pubChemSubstance = pubChemSubstance, 
                    )
                drug.save()
                print("a record is saved")

                # target_list = drug.target.all()

        self.logger.info("COMPLETED CREATING DRUGDATA")
