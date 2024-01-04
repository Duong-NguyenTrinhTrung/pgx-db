from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from drug.models import Drug
from disease.models import Disease

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build disease Data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    diseasedata_data_dir = os.sep.join(
        [str(settings.DATA_DIR), "disease_data"])

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_diseases()
            self.create_disease_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_diseases(self):
        print("checkpoint 1.2 inside purge_diseases function ")
        try:
            Disease.objects.all().delete()
        except Disease.DoesNotExist:
            self.logger.warning(
                "Disease mod not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_diseases function ")

    def create_disease_data(self, filenames=False):
        print("checkpoint 1.4 start of create_disease_data function ")
        self.logger.info("CREATING DISEASEDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.diseasedata_data_dir)
                if fn.endswith("disease_data.csv")
            ]
            print("checkpoint2")
            print(filenames)

        for filename in filenames:

            filepath = os.sep.join([self.diseasedata_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep=";")

            print("data column = ", data.columns)
            for index, row in enumerate(data.iterrows()):

                drug_bankID = data[index: index + 1]["DrugBank_ID"].values[0]
                disease_name = data[index: index + 1]["Disease_name"].values[0]
                disease_class = data[index: index + 1]["Disease_class"].values[0]

                clinical_trial = data[index: index + 1]["Phase"].values[0]
                link = data[index: index +
                                        1]["Link"].values[0]
                standard_inchiKey = data[index: index + 1]["Standard_inchiKey"].values[0]
                disease_UML_CUI = data[index: index + 1]["Disease_UML_CUI"].values[0]

                # fetch drug

                try:
                    d = Drug.objects.get(drug_bankID=drug_bankID)
                except Drug.DoesNotExist:

                    self.logger.error(
                        "Drug not found for entry with drugbank ID {}".format(
                            drug_bankID)
                    )
                    print("Drug not found for entry with drugbank ID {}".format(
                            drug_bankID))
                    continue

                # print("checkpoint 2.1 - start to fetch data to interaction table")
                disease, created = Disease.objects.get_or_create(
                    
                    disease_name = disease_name,
                    disease_class = disease_class,
                    link = link,
                    clinical_trial = clinical_trial,
                    standard_inchiKey = standard_inchiKey,
                    disease_UML_CUI = disease_UML_CUI,
                    drug_bankID = d,
                )
                disease.save()
                # print("a record is saved")

        self.logger.info("COMPLETED CREATING DISEASEDATA")
