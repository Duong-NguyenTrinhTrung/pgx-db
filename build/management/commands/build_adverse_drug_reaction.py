from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from drug.models import Drug, AdverseDrugReaction
from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build adverse drug reaction data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    adr_data_dir = os.sep.join(
        [str(settings.DATA_DIR), "adverse_drug_reaction_data"])

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_adr()
            self.create_dr_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_adr(self):
        print("checkpoint 1.2 inside purge_adr function ")
        try:
            AdverseDrugReaction.objects.all().delete()
        except AdverseDrugReaction.DoesNotExist:
            self.logger.warning(
                "ADR not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_adr function ")

    def create_dr_data(self, filenames=False):
        print("checkpoint 1.4 start of create_dr_data function ")
        self.logger.info("CREATING ADR DATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.adr_data_dir)
                if fn.endswith("SIDER_mapped_matrix_v3.txt")
            ]
            print("checkpoint2")
            print(filenames)

        for filename in filenames:

            filepath = os.sep.join([self.adr_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep="\t")

            side_effects = data.columns[3:]
            for index, row in enumerate(data.iterrows()):

                drug_bankID = data[index: index + 1]["DrugBank_ID"].values[0]
                adr_data = ""
                for se in side_effects[3:]:
                    value = data[index: index + 1][se].values[0]
                    # Stiffiness (10%), Dizziness (5%)
                    if isinstance(value, float) and value>0:
                        adr_data+=se + " (" + str(value) + "%), "

                # fetch drug
                try:
                    d = Drug.objects.get(drug_bankID=drug_bankID)
                except Drug.DoesNotExist:
                    self.logger.error(
                        "Drug not found for entry with drugbank ID {}".format(
                            drug_bankID)
                    )
                    continue

                if adr_data:
                    adr, created = AdverseDrugReaction.objects.get_or_create(
                        drug_bankID = d,
                        adr_data = adr_data,
                    )
                    adr.save()
                    print("a record is saved")

        self.logger.info("COMPLETED CREATING ADR DATA")
