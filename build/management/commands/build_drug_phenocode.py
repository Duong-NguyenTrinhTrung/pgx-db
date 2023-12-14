
from django.core.management.base import BaseCommand
from variant.models import DrugPhenocode, VariantPhenocode
from django.conf import settings
import os
import logging
from django.db.models import Q


class Command(BaseCommand):
    help = 'Add data to the variant coding description'

    # source file directory
    vep_data_dir = os.sep.join([settings.DATA_DIR, "variantphenocode_data"])

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )
    logger = logging.getLogger(__name__)

    def purge_drugphenocode_classs(self):
        try:
            DrugPhenocode.objects.all().delete()
        except DrugPhenocode.DoesNotExist:
            self.logger.warning("DrugPhenocode mod not found: nothing to delete.")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False

        try:
            self.purge_drugphenocode_classs()
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.vep_data_dir)
                if fn.endswith("variantphenocode_data_with_drugname.csv")
            ]
        count=0
        for filename in filenames:
            filepath = os.sep.join([self.vep_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                for line in lines[1:]:
                    values=line[:-1].split(";")
                    phenocode = values[0]
                    coding_description = values[2]
                    drugname = values[-1][0].upper() + values[-1][1:]
                    # print("phenocode:", phenocode, " coding_description:", coding_description, " drugname:", drugname)
                    
                    try:
                            c = VariantPhenocode.objects.get(phenocode=phenocode)
                    except VariantPhenocode.DoesNotExist:

                            self.logger.error(
                                "VariantPhenocode not found for entry with VariantPhenocode {}".format(
                                    phenocode)
                            )
                            continue

                    d, created = DrugPhenocode.objects.get_or_create(
                        coding_description=coding_description,
                        drugname_in_coding_description=drugname,
                        phenocode=c
                        )
                    d.save()





