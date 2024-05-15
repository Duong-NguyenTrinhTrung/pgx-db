from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from drug.models import SideEffect
from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build side effect data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    se_data_dir = os.sep.join(
        [str(settings.DATA_DIR), "adverse_drug_reaction_data"])

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_se()
            self.create_se_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_se(self):
        print("checkpoint 1.2 inside purge_se function ")
        try:
            SideEffect.objects.all().delete()
        except SideEffect.DoesNotExist:
            self.logger.warning(
                "SE not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_se function ")

    def create_se_data(self, filenames=False):
        print("checkpoint 1.4 start of create_se_data function ")
        self.logger.info("CREATING SE DATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.se_data_dir)
                if fn.endswith("Side_effect_definition.csv")
            ]
            print("checkpoint2")
            print(filenames)

        for filename in filenames:

            filepath = os.sep.join([self.se_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep="\t")

            for index, row in enumerate(data.iterrows()):

                se = data[index: index + 1]["Side_effect"].values[0]
                definition = data[index: index + 1]["Definition"].values[0]
                se, created = SideEffect.objects.get_or_create(
                    side_effect_name = se,
                    side_effect_definition = definition,
                )
                se.save()
                print("a record is saved")

        self.logger.info("COMPLETED CREATING SE DATA")
