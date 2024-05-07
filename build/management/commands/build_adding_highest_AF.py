
from django.core.management.base import BaseCommand
from variant.models import VepVariant
from django.conf import settings
import os
import logging
from django.db.models import Q
import numpy as np


class Command(BaseCommand):
    help = 'Add data to the VEPVariant HighestAF column'

    # source file directory
    vep_data_dir = os.sep.join([settings.DATA_DIR, "vep_variant_data"])

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
                for fn in os.listdir(self.vep_data_dir)
                if fn.endswith("20230506-SNV_marker_only_with_highest_AF.csv")
            ]
            print(filenames)
        count=0
        for filename in filenames:
            filepath = os.sep.join([self.vep_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    values=line[:-1].split(";")
                    variant_marker = values[1]
                    transcript_id = values[2]
                    highest_af = values[-1]
                    # print("variant_marker = ",variant_marker)
                    # print("transcript_id = ",transcript_id)
                    # Code to add values to the new field
                    try:
                        obj = VepVariant.objects.get(
                            Q(Variant_marker=variant_marker) & Q(Transcript_ID=transcript_id)
                        )
                        if highest_af=="":
                            obj.HighestAF = np.nan
                        else:
                            obj.HighestAF = float(highest_af)
                        obj.save()
                    except VepVariant.DoesNotExist:
                        # Handle the case when the object does not exist
                        print(f"Object not found for Variant_marker: {variant_marker} and Transcript_ID: {transcript_id}")
                        count+=1
        print("---- end of adding data, number of case not found: ", count)



