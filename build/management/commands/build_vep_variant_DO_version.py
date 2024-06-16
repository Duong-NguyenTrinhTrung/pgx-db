from django.core.management.base import BaseCommand, CommandError
from django.conf import settings

from variant.models import Variant, VepVariant

import logging
import os
import pandas as pd


class Command(BaseCommand):
    help = "Build Genebass VEP Data"

    def add_arguments(self, parser):
        parser.add_argument(
            "--filename",
            action="append",
            dest="filename",
            help="Filename to import. Can be used multiple times",
        )

    logger = logging.getLogger(__name__)

    # source file directory
    vepvariant_data_dir = os.sep.join(
        [settings.DATA_DIR, "vep_variant_data"])

    def handle(self, *args, **options):
        if options["filename"]:
            filenames = options["filename"]
        else:
            filenames = False
        print(f"Data file to import: {filenames}")

        try:
            self.purge_vep_variant()
            self.create_vepvariant_data(filenames)
        except Exception as msg:
            print(msg)
            self.logger.error(msg)

    def purge_vep_variant(self):
        print("Purge VepVariant data")
        try:
            VepVariant.objects.all().delete()
        except VepVariant.DoesNotExist:
            self.logger.warning(
                "Vep mod not found: nothing to delete.")

        print("End purge VepVariant data")

    def create_vepvariant_data(self, filenames=False):
        print("Start creating vep variant data")

        # read source files
        if not filenames:
            filenames = [
                fn
                for fn in os.listdir(self.vepvariant_data_dir)
                if fn.startswith("vep_variant_data_wo_alpha_missense_part")
            ]

        for filename in filenames:
            print(f"{filename} is processing")
            filepath = os.sep.join(
                [self.vepvariant_data_dir, filename])

            data = pd.read_csv(filepath, low_memory=False,
                               encoding="ISO-8859-1", sep=";")

            print(f"Total records {len(data)}")

            # Create batch objects at a time
            batch = 100
            times = int(len(data) / batch)
            for i in range(times):
                print(f"Bulk creating {i * batch} to {(i + 1) * batch}")
                self.__bulk_create_vep_variant_records(data[i * batch: (i + 1) * batch])
            
            mod = len(data)%batch
            print(f"Bulk creating {len(data)-mod+1} to {len(data)}")
            self.__bulk_create_vep_variant_records(data[len(data)-mod+1: len(data)])

        print("End of VEP Variant data import")

    @staticmethod
    def __bulk_create_vep_variant_records(data):
        objects = []

        # variant_ids = Command.__get_variant_marker_ids(data)
        for index, row in enumerate(data.iterrows()):
            Variant_marker = data[index: index + 1]["Variant_marker"].values[0]
            Transcript_ID = data[index: index + 1]["Transcript_ID"].values[0]
            Consequence = data[index: index + 1]["Consequence"].values[0]
            cDNA_position = data[index: index + 1]["cDNA_position"].values[0]
            CDS_position = data[index: index + 1]["CDS_position"].values[0]
            Protein_position = data[index: index + 1]["Protein_position"].values[0]
            Amino_acids = data[index: index + 1]["Amino_acids"].values[0]
            Codons = data[index: index + 1]["Codons"].values[0]
            Impact = data[index: index + 1]["Impact"].values[0]
            Strand = data[index: index + 1]["Strand"].values[0]
            BayesDel_addAF_rankscore = data[index: index + 1]["BayesDel_addAF_rankscore"].values[0]
            BayesDel_noAF_rankscore = data[index: index + 1]["BayesDel_noAF_rankscore"].values[0]
            CADD_raw_rankscore = data[index: index + 1]["CADD_raw_rankscore"].values[0]
            ClinPred_rankscore = data[index: index + 1]["ClinPred_rankscore"].values[0]
            DANN_rankscore = data[index: index + 1]["DANN_rankscore"].values[0]
            DEOGEN2_rankscore = data[index: index + 1]["DEOGEN2_rankscore"].values[0]
            Eigen_PC_raw_coding_rankscore = data[index: index + 1]["Eigen_PC_raw_coding_rankscore"].values[0]
            Eigen_raw_coding_rankscore = data[index: index + 1]["Eigen_raw_coding_rankscore"].values[0]
            FATHMM_converted_rankscore = data[index: index + 1]["FATHMM_converted_rankscore"].values[0]
            GERP_RS_rankscore = data[index: index + 1]["GERP_RS_rankscore"].values[0]
            GM12878_fitCons_rankscore = data[index: index + 1]["GM12878_fitCons_rankscore"].values[0]
            GenoCanyon_rankscore = data[index: index + 1]["GenoCanyon_rankscore"].values[0]
            H1_hESC_fitCons_rankscore = data[index: index + 1]["H1_hESC_fitCons_rankscore"].values[0]
            HUVEC_fitCons_rankscore = data[index: index + 1]["HUVEC_fitCons_rankscore"].values[0]
            LIST_S2_rankscore = data[index: index + 1]["LIST_S2_rankscore"].values[0]
            LRT_converted_rankscore = data[index: index + 1]["LRT_converted_rankscore"].values[0]
            M_CAP_rankscore = data[index: index + 1]["M_CAP_rankscore"].values[0]
            MPC_rankscore = data[index: index + 1]["MPC_rankscore"].values[0]
            MVP_rankscore = data[index: index + 1]["MVP_rankscore"].values[0]
            MetaLR_rankscore = data[index: index + 1]["MetaLR_rankscore"].values[0]
            MetaRNN_rankscore = data[index: index + 1]["MetaRNN_rankscore"].values[0]
            MetaSVM_rankscore = data[index: index + 1]["MetaSVM_rankscore"].values[0]
            MutPred_rankscore = data[index: index + 1]["MutPred_rankscore"].values[0]
            MutationAssessor_rankscore = data[index: index + 1]["MutationAssessor_rankscore"].values[0]
            MutationTaster_converted_rankscore = \
                data[index: index + 1]["MutationTaster_converted_rankscore"].values[0]
            PROVEAN_converted_rankscore = data[index: index + 1]["PROVEAN_converted_rankscore"].values[0]
            Polyphen2_HDIV_rankscore = data[index: index + 1]["Polyphen2_HDIV_rankscore"].values[0]
            Polyphen2_HVAR_rankscore = data[index: index + 1]["Polyphen2_HVAR_rankscore"].values[0]
            PrimateAI_rankscore = data[index: index + 1]["PrimateAI_rankscore"].values[0]
            REVEL_rankscore = data[index: index + 1]["REVEL_rankscore"].values[0]
            SIFT4G_converted_rankscore = data[index: index + 1]["SIFT4G_converted_rankscore"].values[0]
            SIFT_converted_rankscore = data[index: index + 1]["SIFT_converted_rankscore"].values[0]
            SiPhy_29way_logOdds_rankscore = data[index: index + 1]["SiPhy_29way_logOdds_rankscore"].values[0]
            VEST4_rankscore = data[index: index + 1]["VEST4_rankscore"].values[0]
            bStatistic_converted_rankscore = data[index: index + 1]["bStatistic_converted_rankscore"].values[0]
            Fathmm_MKL_coding_rankscore = data[index: index + 1]["Fathmm_MKL_coding_rankscore"].values[0]
            Fathmm_XF_coding_rankscore = data[index: index + 1]["Fathmm_XF_coding_rankscore"].values[0]
            Integrated_fitCons_rankscore = data[index: index + 1]["Integrated_fitCons_rankscore"].values[0]
            PhastCons30way_mammalian_rankscore = \
                data[index: index + 1]["PhastCons30way_mammalian_rankscore"].values[0]
            PhyloP30way_mammalian_rankscore = data[index: index + 1]["PhyloP30way_mammalian_rankscore"].values[0]
            LINSIGHT_rankscore = data[index: index + 1]["LINSIGHT_rankscore"].values[0]

            # This could be done better
            try:
                vm = Variant.objects.get(
                    VariantMarker=Variant_marker)
            except Variant.DoesNotExist:
                continue

            # variant_id = variant_ids[Variant_marker]

            objects.append(
                VepVariant(
                    Variant_marker_id=vm.VariantMarker,
                    Transcript_ID=Transcript_ID,
                    Consequence=Consequence,
                    cDNA_position=cDNA_position,
                    CDS_position=CDS_position,
                    Protein_position=Protein_position,
                    Amino_acids=Amino_acids,
                    Codons=Codons,
                    Impact=Impact,
                    Strand=Strand,
                    BayesDel_addAF_rankscore=BayesDel_addAF_rankscore,
                    BayesDel_noAF_rankscore=BayesDel_noAF_rankscore,
                    CADD_raw_rankscore=CADD_raw_rankscore,
                    ClinPred_rankscore=ClinPred_rankscore,
                    DANN_rankscore=DANN_rankscore,
                    DEOGEN2_rankscore=DEOGEN2_rankscore,
                    Eigen_PC_raw_coding_rankscore=Eigen_PC_raw_coding_rankscore,
                    Eigen_raw_coding_rankscore=Eigen_raw_coding_rankscore,
                    FATHMM_converted_rankscore=FATHMM_converted_rankscore,
                    GERP_RS_rankscore=GERP_RS_rankscore,
                    GM12878_fitCons_rankscore=GM12878_fitCons_rankscore,
                    GenoCanyon_rankscore=GenoCanyon_rankscore,
                    H1_hESC_fitCons_rankscore=H1_hESC_fitCons_rankscore,
                    HUVEC_fitCons_rankscore=HUVEC_fitCons_rankscore,
                    LIST_S2_rankscore=LIST_S2_rankscore,
                    LRT_converted_rankscore=LRT_converted_rankscore,
                    M_CAP_rankscore=M_CAP_rankscore,
                    MPC_rankscore=MPC_rankscore,
                    MVP_rankscore=MVP_rankscore,
                    MetaLR_rankscore=MetaLR_rankscore,
                    MetaRNN_rankscore=MetaRNN_rankscore,
                    MetaSVM_rankscore=MetaSVM_rankscore,
                    MutPred_rankscore=MutPred_rankscore,
                    MutationAssessor_rankscore=MutationAssessor_rankscore,
                    MutationTaster_converted_rankscore=MutationTaster_converted_rankscore,
                    PROVEAN_converted_rankscore=PROVEAN_converted_rankscore,
                    Polyphen2_HDIV_rankscore=Polyphen2_HDIV_rankscore,
                    Polyphen2_HVAR_rankscore=Polyphen2_HVAR_rankscore,
                    PrimateAI_rankscore=PrimateAI_rankscore,
                    REVEL_rankscore=REVEL_rankscore,
                    SIFT4G_converted_rankscore=SIFT4G_converted_rankscore,
                    SIFT_converted_rankscore=SIFT_converted_rankscore,
                    SiPhy_29way_logOdds_rankscore=SiPhy_29way_logOdds_rankscore,
                    VEST4_rankscore=VEST4_rankscore,
                    bStatistic_converted_rankscore=bStatistic_converted_rankscore,
                    Fathmm_MKL_coding_rankscore=Fathmm_MKL_coding_rankscore,
                    Fathmm_XF_coding_rankscore=Fathmm_XF_coding_rankscore,
                    Integrated_fitCons_rankscore=Integrated_fitCons_rankscore,
                    PhastCons30way_mammalian_rankscore=PhastCons30way_mammalian_rankscore,
                    PhyloP30way_mammalian_rankscore=PhyloP30way_mammalian_rankscore,
                    LINSIGHT_rankscore=LINSIGHT_rankscore
                )
            )

        VepVariant.objects.bulk_create(objects)

    @staticmethod
    def __get_variant_marker_ids(data):
        variant_markers = []
        for index, row in data.iterrows():
            variant_markers.append(row["Variant_marker"])

        variant_marker_ids = Variant.objects \
            .filter(VariantMarker__in=variant_markers) \
            .values("VariantMarker") \
            .distinct()

        print(f"variant_marker_ids: \n {variant_marker_ids}")
        return variant_marker_ids
