
from django.core.management.base import BaseCommand
from protein.models import Protein
from django.conf import settings
import os
import logging

class Command(BaseCommand):
    help = 'Add data to the protein class column'

    # source file directory
    protein_data_dir = os.sep.join([settings.DATA_DIR, "protein_data"])

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
                for fn in os.listdir(self.protein_data_dir)
                if fn.endswith("protein_data_with_protein_class.csv")
            ]
            print(filenames)
        count=0
        for filename in filenames:
            filepath = os.sep.join([self.protein_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    values=line[:-1].split(";")
                    protein_id = values[0]
                    protein_class = values[-1]

                    # Code to add values to the new field
                    obj = Protein.objects.get(uniprot_ID=protein_id)
                    obj.Protein_class = protein_class
                    obj.save()
                    print(protein_id, " with class is saved")


