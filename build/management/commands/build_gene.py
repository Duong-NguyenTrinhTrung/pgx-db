# build_drug.py
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings


from gene.models import Gene

from optparse import make_option
import logging
import csv
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Gene Data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    genedata_data_dir = os.sep.join([settings.DATA_DIR, "gene_primary_transcript_data"])

    print("checkpoint1")

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print("checkpoint 1.1, filenames = ", filenames)

        try:
            self.purge_genes()
            self.create_gene_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_genes(self):
        print("checkpoint 1.2 inside purge_genes function ")
        try:
            Gene.objects.all().delete()
        except Gene.DoesNotExist:
            self.logger.warning("Gene not found: nothing to delete.")

        print("checkpoint 1.3 end of purge_genes function ")

    def create_gene_data(self, filenames=False):
        print("checkpoint 1.4 start of create_gene_data function ")
        self.logger.info("CREATING GENEDATA")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.genedata_data_dir)
                if fn.endswith("gene_primary_transcript_data.csv")
            ]
            print("checkpoint2")
            print(filenames)

       
            
        #read the gene data
        for filename in filenames:

            filepath = os.sep.join([self.genedata_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep=";")
            data.dropna(subset=["GeneID"], inplace=True)
            
            # print("checkpoint 2.1 - start to fetch data to Gene table")

            for index, row in enumerate(data.iterrows()):

                gene_id = data[index: index + 1]["GeneID"].values[0]
                genename = data[index: index + 1]["Gene name"].values[0]
                pt = data[index: index + 1]["Primary_transcript"].values[0]
                

                gene, created = Gene.objects.get_or_create(
                    gene_id=gene_id,
                    genename=genename,
                    primary_transcript=pt,
                    )
                gene.save()
                print("a record is saved")

                # target_list = drug.target.all()

        self.logger.info("COMPLETED CREATING GENEDATA")
