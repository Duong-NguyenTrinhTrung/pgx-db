# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from variant.models import VariantMapper
from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Variant Mapping Data"
    variant_mapping_data_dir = os.sep.join([settings.DATA_DIR, "RefSeq/HumanGRCh38"])


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
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            # self.purge_variant_mapping()
            self.create_variant_mapping_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_variant_mapping(self):
        print("checkpoint 1.2 inside purge_variant_mapping function ")
        try:
            VariantMapper.objects.all().delete()
        except VariantMapper.DoesNotExist:
            self.logger.warning("VariantMapper mod not found: nothing to delete.")
        print("checkpoint 1.3 end of purge_variant_mapping function ")

   

    def create_variant_mapping_data(self, filenames=False):
        self.logger.info("CREATING VARIANT MAPPING DATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.variant_mapping_data_dir)
                if fn.startswith("ALL_ConvertedVM_Refseq")
            ]
            print(sorted(filenames))
        batch = 100000
        for filename in sorted(filenames):
            filepath = os.sep.join([self.variant_mapping_data_dir, filename])
            objects = []
            with open(filepath, "r") as f:
                lines = f.readlines()
                #;GeneratedVM;rsID
                index=1
                last = len(lines)-len(lines)%batch
                print("len = ", len(lines), " last = ",last)
                for line in lines[1:last+1]:
                    values=line[:-1].split(";")
                    ensembl = values[0]
                    refseq  = values[1]
                    objects.append(VariantMapper(
                                genome_version = "38",
                                ensembl = ensembl,
                                refseq  = refseq,
                            ))
                    if len(objects)==batch: 
                        VariantMapper.objects.bulk_create(objects)
                        print(filename, ", bunch ", index," --> ", index+batch)
                        index+=batch
                        objects = []
                # don't forget the last bunch
                # for line in lines[last+1:]:
                #     values=line[:-1].split(";")
                #     ensembl = values[0]
                #     refseq  = values[1]
                #     objects.append(VariantMapper(
                #                 genome_version = "38",
                #                 ensembl = ensembl,
                #                 refseq  = refseq,
                #             ))
                #     VariantMapper.objects.bulk_create(objects)
                #     print(filename, ", last bunch ", last+1," --> ", len(lines))
                        
            print("all records inserted")
        self.logger.info("COMPLETED CREATING VARIANT MAPPER DATA")
