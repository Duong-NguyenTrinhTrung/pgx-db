
from django.core.management.base import BaseCommand
from drug.models import Drug
from django.conf import settings
import os
import logging

class Command(BaseCommand):
    help = 'Add data to the clinical status column'

    # source file directory
    drug_data_dir = os.sep.join([settings.DATA_DIR, "drug_data"])

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )
    logger = logging.getLogger(__name__)

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.drug_data_dir)
                if fn.endswith("drug_data_Zia.csv")
            ]
            print(filenames)
        count=0
        for filename in filenames:
            filepath = os.sep.join([self.drug_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    values=line[:-1].split(";")
                    drug_bankID = values[0]
                    print("drug_bankID = ",drug_bankID)
                    clinical_status = values[1]

                    # Code to add values to the new field
                    obj = Drug.objects.get(drug_bankID=drug_bankID)
                    obj.Clinical_status = clinical_status
                    obj.save()
                    print(drug_bankID, " with clinical_status is saved")


