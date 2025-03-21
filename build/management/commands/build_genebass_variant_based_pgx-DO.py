
from django.core.management.base import BaseCommand, CommandError
from django.conf import settings
from drug.models import Drug
from gene.models import Gene
from variant.models import GenebassVariantPGx, VariantPhenocode, Variant
from optparse import make_option
import logging
import csv
import os
import pandas as pd


def convert_vm(vm): # from chr7:151048886_A/G to 3_87991616_G/A
    p1=vm.split(":")[0]
    p2=vm.split(":")[1]
    return p1[3:]+"_"+p2
    
class Command(BaseCommand):
    help = "Build genebass pgx data"

    # source file directory
    vb_pgx_data_dir = os.sep.join([settings.DATA_DIR, "genebass_variant_data"])

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
        # print("checkpoint 1.1, filenames = ", filenames)

        try:
            # self.purge_vb_pgx_classs()
            self.create_gb_pgx_class_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_vb_pgx_classs(self):
        try:
            GenebassVariantPGx.objects.all().delete()
        except GenebassVariantPGx.DoesNotExist:
            self.logger.warning("GenebassVariantPGx mod not found: nothing to delete.")

    def create_gb_pgx_class_data(self, filenames=False):
        self.logger.info("CREATING GenebassVariantPGx")


        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.vb_pgx_data_dir)
                if fn.endswith("variant_genebassvariantpgx.csv")
            ]
        

            for i, filename in enumerate(filenames):
                    filepath = os.sep.join([self.vb_pgx_data_dir, filename])
                    data = pd.read_csv(filepath, low_memory=False,
                                    encoding="ISO-8859-1", sep=";;")
                    pgx_objects = []
                    for index, row in enumerate(data.iterrows()):
                        genename = data[index: index + 1]["genename"].values[0]
                        markerID = convert_vm(data[index: index + 1]["variant_marker_id"].values[0])
                        annotation = data[index: index + 1]["annotation"].values[0]
                        n_cases = data[index: index + 1]["n_cases"].values[0]
                        n_controls = data[index: index + 1]["n_controls"].values[0]
                        # phenocode = data[index: index + 1]["phenocode"].values[0]
                        description = data[index: index + 1]["description"].values[0]
                        coding_description = data[index: index + 1]["coding_description"].values[0]
                        Pvalue = data[index: index + 1]["Pvalue"].values[0]
                        AC = data[index: index + 1]["AC"].values[0]
                        AF = data[index: index + 1]["AF"].values[0]
                        BETA = data[index: index + 1]["BETA"].values[0]
                        drugbank_id = data[index: index + 1]["drugbank_id_id"].values[0]

                        # fetch gene
                        try:
                            g = Gene.objects.get(genename=genename)
                        except Gene.DoesNotExist:

                            self.logger.error(
                                "Gene not found for genename {}".format(
                                    genename)
                            )
                            f.write("\nGene not found for genename {}".format(genename))
                            continue

                        # fetch variant
                        try:
                            vm = Variant.objects.get(VariantMarker=markerID)
                        except Variant.DoesNotExist:

                            # self.logger.error(
                            #     "Variant not found for Variant marker {}".format(
                            #         markerID)
                            # )
                            # f.write("Variant not found for Variant marker {}".format(markerID))
                            continue

                        # fetch drug
                        try:
                            d = Drug.objects.get(drug_bankID=drugbank_id)
                        except Drug.DoesNotExist:

                            self.logger.error(
                                "Drug not found for drugname {}".format(
                                    drugname)
                            )
                            f.write("\nDrug not found for drugname {}".format(drugname))
                            continue

                        pgx = GenebassVariantPGx(
                            genename=g.genename,
                            variant_marker=vm,
                            annotation=annotation,
                            n_cases=n_cases,
                            n_controls=n_controls,
                            # phenocode=p,
                            description=description,
                            coding_description=coding_description,
                            Pvalue=Pvalue,
                            BETA=BETA,
                            AC=AC,
                            AF=AF,
                            drugbank_id=d,
                        )
                        pgx_objects.append(pgx)
                        if (len(pgx_objects)==1000):

                            GenebassVariantPGx.objects.bulk_create(pgx_objects)
                            print("up to ", i+1, " objects have been created")
                            pgx_objects = []

                    # last portion 
                    GenebassVariantPGx.objects.bulk_create(pgx_objects)

                    