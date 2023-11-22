
from django.core.management.base import BaseCommand
from variant.models import GenebassCategory
from django.conf import settings
import os
import logging

class Command(BaseCommand):
    help = 'Add data to the protein class column'

    # source file directory
    gb_category_data_dir = os.sep.join([settings.DATA_DIR, "genebass_category_data"])

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )
    logger = logging.getLogger(__name__)

    def purge_gb_cate(self):
        try:
            GenebassCategory.objects.all().delete()
        except GenebassCategory.DoesNotExist:
            self.logger.warning("GenebassCategory not found: nothing to delete.")


    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False

        try:
            self.purge_gb_cate()
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.gb_category_data_dir)
                if fn.endswith("genebass_category_data.csv")
            ]
            print(filenames)
        count=0
        for filename in filenames:
            filepath = os.sep.join([self.gb_category_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines:
                    values=line[:-1].split(";")
                    category_code = values[0]
                    category_description = values[1]

                    # Code to add values to the new field
                    obj = GenebassCategory()
                    obj.category_code = category_code
                    obj.category_description = category_description
                    obj.save()
                    print("a new category is saved")


