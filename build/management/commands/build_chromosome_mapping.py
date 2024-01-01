# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from chromosome.models import Chromosome

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Chromosome Data"
    chromosomedata_data_dir = os.sep.join([settings.DATA_DIR, "ChromosomeMapping/ChromosomeMappings"])


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
            self.purge_chromosome()
            self.create_chromosome_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_chromosome(self):
        print("checkpoint 1.2 inside purge_chromosome function ")
        try:
            Chromosome.objects.all().delete()
        except Chromosome.DoesNotExist:
            self.logger.warning("Chromosomes mod not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_chromosome function ")

   

    def create_chromosome_data(self, filenames=False):
        self.logger.info("CREATING CHROMOSOME")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.chromosomedata_data_dir)
                if fn.endswith("HumanChromosomeMappingData.csv")
            ]
            print(filenames)
        
        for filename in filenames:
            filepath = os.sep.join([self.chromosomedata_data_dir, filename])
            with open(filepath, "r") as f:
                lines = f.readlines()
                #;version;NCBI;UCSC;ensembl;gencode;RefSeq
                for i,line in enumerate(lines[1:]):
                        values=line[:-1].split(";")
                        version = values[1]
                        NCBI = values[2]
                        UCSC = values[3]
                        ensembl = values[4]
                        gencode = values[5]
                        RefSeq  = values[6]

                        type, created = Chromosome.objects.get_or_create(
                            genome_version = version,
                            ncbi = NCBI,
                            ucsc = UCSC,
                            ensembl = ensembl,
                            gencode = gencode,
                            refseq  = RefSeq,
                            )
                        type.save()
                        print(i, " a record is saved")


        self.logger.info("COMPLETED CREATING CHROMOSOME DATA")
