# build_protein.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from protein.models import Protein

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Protein Data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    proteindata_data_dir = os.sep.join([settings.DATA_DIR, "protein_data"])

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_proteins()
            self.create_protein_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_proteins(self):
        print("checkpoint 1.2 inside purge_proteins function ")
        try:
            Protein.objects.all().delete()
        except Protein.DoesNotExist:
            self.logger.warning("Protein mod not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_proteins function ")

    def create_protein_data(self, filenames=False):
        print("checkpoint 1.4 start of create_protein_data function ")
        self.logger.info("CREATING PROTEINDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.proteindata_data_dir)
                if fn.endswith("protein_data.csv")
            ]
            print("checkpoint2")
            print(filenames)

        for filename in filenames:

            filepath = os.sep.join([self.proteindata_data_dir, filename])

            data = pd.read_csv(
                filepath, low_memory=False,
                encoding="ISO-8859-1",
            )

            for index, row in enumerate(data.iterrows()):

                uniprot_ID = data[index: index + 1]["uniprot_ID"].values[0]
                genename = data[index: index + 1]["genename"].values[0]
                geneID = data[index: index + 1]["geneID"].values[0]

                entry_name = data[index: index + 1]["entry_name"].values[0]
                protein_name = data[index: index + 1]["protein_name"].values[0]
                sequence = data[index: index + 1]["sequence"].values[0]

                # # fetch protein
                # try:
                #     p = Protein.objects.get(entry_name=entry_name)
                # except Protein.DoesNotExist:

                #     self.logger.error(
                #         "Protein not found for entry_name {}".format(
                #             entry_name)
                #     )
                #     continue

                # print("checkpoint 2.1 - start to fetch data to Protein table")
                protein, created = Protein.objects.get_or_create(
                    uniprot_ID=uniprot_ID,
                    genename=genename,
                    geneID=geneID,
                    entry_name=entry_name,
                    protein_name=protein_name,
                    sequence=sequence,
                )
                protein.save()
                print("a record is saved")

        self.logger.info("COMPLETED CREATING PROTEINDATA")
