from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from drug.models import Drug
from disease.models import Disease, DrugDiseaseStudy
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
            self.purge_drug_disease_study()
            self.create_disease_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_drug_disease_study(self):
        print("checkpoint 1.2 inside purge_diseases function ")
        try:
            DrugDiseaseStudy.objects.all().delete()
        except DrugDiseaseStudy.DoesNotExist:
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
                if fn.endswith("disease_drug_study_data.csv")
            ]
            print("checkpoint2")
            print(filenames)

        for filename in filenames:

            filepath = os.sep.join([self.diseasedata_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep=";")

            print("data column = ", data.columns)
            for index, row in enumerate(data.iterrows()):
                Disease_name = data[index: index + 1]["Disease_name"].values[0]
                Phase = data[index: index + 1]["Phase"].values[0]
                Standard_inchiKey = data[index: index + 1]["Standard_inchiKey"].values[0]
                Link = data[index: index + 1]["Link"].values[0]
                drug_bankID = data[index: index + 1]["DrugBank_ID"].values[0]

                # fetch disease
                try:
                    # print(Disease_name, " is got")
                    di = Disease.objects.get(disease_name=Disease_name)
                except Disease.DoesNotExist:

                    self.logger.error(
                        "Disease not found for entry with Disease name {}".format(
                            Disease_name)
                    )
                    print("Disease not found for entry with Disease_name {}".format(
                            Disease_name))
                    continue

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
                disease, created = DrugDiseaseStudy.objects.get_or_create(
                    
                    disease_name = di,
                    clinical_trial = Phase,
                    standard_inchiKey = Standard_inchiKey,
                    link = Link,
                    drug_bankID = d,
                )
                disease.save()
                # print("a record is saved")

        self.logger.info("COMPLETED CREATING DRUG DISEASE STUDY DATA")
