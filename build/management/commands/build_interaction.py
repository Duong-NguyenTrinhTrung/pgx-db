# build_interaction.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from interaction.models import Interaction
from drug.models import Drug
from protein.models import Protein

from optparse import make_option
import logging
import csv
import os
import pandas as pd


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
    interactiondata_data_dir = os.sep.join(
        [str(settings.DATA_DIR), "interaction_data"])
    # interactiondata_data_dir = settings.DATA_DIR / "interaction_data"

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_interactions()
            self.create_interaction_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_interactions(self):
        print("checkpoint 1.2 inside purge_interactions function ")
        try:
            Interaction.objects.all().delete()
        except Interaction.DoesNotExist:
            self.logger.warning(
                "Interaction mod not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_interactions function ")

    def create_interaction_data(self, filenames=False):
        print("checkpoint 1.4 start of create_interaction_data function ")
        self.logger.info("CREATING INTERACTIONDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.interactiondata_data_dir)
                if fn.endswith("interaction_data.csv")
            ]
            print("checkpoint2")
            print(filenames)

        for filename in filenames:

            filepath = os.sep.join([self.interactiondata_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep=";")

            print("data length = ", len(data))
            print("data column = ", data.columns)
            for index, row in enumerate(data.iterrows()):

                drug_bankID = data[index: index + 1]["drug_bankID"].values[0]
                uniprot_ID = data[index: index + 1]["uniprot_ID"].values[0]
                actions = data[index: index + 1]["actions"].values[0]

                known_action = data[index: index + 1]["known_action"].values[0]
                interaction_type = data[index: index +
                                        1]["interaction_type"].values[0]
                pubmed_ids = data[index: index + 1]["pubmed_ids"].values[0]

                # fetch drug

                try:
                    d = Drug.objects.get(drug_bankID=drug_bankID)
                except Drug.DoesNotExist:

                    self.logger.error(
                        "Drug not found for entry with drugbank ID {}".format(
                            drug_bankID)
                    )
                    continue

                # fetch protein data
                try:
                    p = Protein.objects.get(uniprot_ID=uniprot_ID)
                except Protein.DoesNotExist:

                    self.logger.error(
                        "Protein not found for entry with uniprot ID {}".format(
                            uniprot_ID)
                    )
                    continue

                # print("checkpoint 2.1 - start to fetch data to interaction table")
                interaction, created = Interaction.objects.get_or_create(
                    drug_bankID=d,
                    uniprot_ID=p,
                    actions=actions,
                    known_action=known_action,
                    interaction_type=interaction_type,
                    # atc_codes=atc_codes,
                    pubmed_ids=pubmed_ids,
                    # ChEMBL=ChEMBL,
                )
                interaction.save()
                print("a record is saved")

        self.logger.info("COMPLETED CREATING INTERACTIONDATA")
