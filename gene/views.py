import decimal
import random
import warnings
from django.core.cache import cache
from django.db.models import (
    F,
    IntegerField,
)
from django.db.models.functions import Cast
from django.http import (
    HttpResponseBadRequest,
    JsonResponse,
)
from django.views import View
from django.views.decorators.http import require_http_methods
from django.views.generic import TemplateView
from django.shortcuts import render
import numpy as np
import pandas as pd
import json
from gene.models import Gene
from protein.models import Protein
from interaction.models import Interaction
from drug.models import Drug 
from variant.models import (
    GenebassVariant,
    Variant,
    VepVariant,
    GenebassCategory,
    VariantPhenocode
)
import urllib.request as urlreq
import urllib.request as urlreq
from django.shortcuts import render
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import (
    Count,
    Q,
)

warnings.filterwarnings('ignore')

list_necessary_columns = [
    "Transcript_ID",
    "Consequence",
    "cDNA_position",
    "CDS_position",
    "Protein_position",
    "Amino_acids",
    "Codons",
    "Impact",
    "Strand",
    "BayesDel_addAF_rankscore",
    "BayesDel_noAF_rankscore",
    "CADD_raw_rankscore",
    "ClinPred_rankscore",
    "DANN_rankscore",
    "DEOGEN2_rankscore",
    "Eigen_PC_raw_coding_rankscore",
    "Eigen_raw_coding_rankscore",
    "FATHMM_converted_rankscore",
    "GERP_RS_rankscore",
    "GM12878_fitCons_rankscore",
    "GenoCanyon_rankscore",
    "H1_hESC_fitCons_rankscore",
    "HUVEC_fitCons_rankscore",
    "LIST_S2_rankscore",
    "LRT_converted_rankscore",
    "M_CAP_rankscore",
    "MPC_rankscore",
    "MVP_rankscore",
    "MetaLR_rankscore",
    "MetaRNN_rankscore",
    "MetaSVM_rankscore",
    "MutPred_rankscore",
    "MutationAssessor_rankscore",
    "MutationTaster_converted_rankscore",
    "PROVEAN_converted_rankscore",
    "Polyphen2_HDIV_rankscore",
    "Polyphen2_HVAR_rankscore",
    "PrimateAI_rankscore",
    "REVEL_rankscore",
    "SIFT4G_converted_rankscore",
    "SIFT_converted_rankscore",
    "SiPhy_29way_logOdds_rankscore",
    "VEST4_rankscore",
    "bStatistic_converted_rankscore",
    "Fathmm_MKL_coding_rankscore",
    "Fathmm_XF_coding_rankscore",
    "Integrated_fitCons_rankscore",
    "PhastCons30way_mammalian_rankscore",
    "PhyloP30way_mammalian_rankscore",
    "AM_pathogenicity",
    "HighestAF",
]

browser_columns = ["Variant_marker"] + list_necessary_columns

list_necessary_columns_2 = ["Transcript_ID", "Consequence", "Protein_position", "Amino_acids", "Codons", "HighestAF"] + list_necessary_columns[9:-1]

name_dic = {'NMD': 'NMD_transcript', 'cse': 'coding_sequence', 'fsh': 'frameshift',
            'itc': 'incomplete_terminal_codon', 'ide': 'inframe_deletion', 'iis': 'inframe_insertion',
            'mis': 'missense', 'pal': 'protein_altering', 'sac': 'splice_acceptor', 'sdo': 'splice_donor',
            'sd5': 'splice_donor_5th_base', 'sdr': 'splice_donor_region',
            'spt': 'splice_polypyrimidine_tract', 'sre': 'splice_region', '_sl': 'start_lost',
            '_sr': 'start_retained', 'sga': 'stop_gained', 'sl_': 'stop_lost', 'sr_': 'stop_retained',
            'syn': 'synonymous', 'H': 'high', 'M': 'Medium', 'L': 'Low'}

# this is for API call
class BasicVariantAnnotationFromGeneIDView(object):
    list_necessary_columns = [
        "Transcript_ID",
        "Consequence",
        "cDNA_position",
        "CDS_position",
        "Protein_position",
        "Amino_acids",
        "Codons",
        "Impact",
        "Strand",
        "HighestAF"]
    
    def get_basic_annotation_for_all_variant_by_gene(self, slug):
        
        context = {}
        if slug is not None:
            print("slug not none ", slug)
            if cache.get("get_basic_annotation_for_all_variant_by_gene_data_" + slug) is not None:
                data = cache.get("get_basic_annotation_for_all_variant_by_gene_data_" + slug)
            else:
                try:
                    results = []
                    primary_ts = Gene.objects.get(gene_id=slug).primary_transcript
                    data = VepVariant.objects.filter(Transcript_ID=primary_ts).values_list(*list_necessary_columns)
                    for i, item in enumerate(data):
                        consequence_list = item[1].split(",")
                        t = [name_dic.get(c) for c in consequence_list]

                        results.append({
                            "Transcript_ID": item[0],
                            "Consequence": ",".join(t),
                            "cDNA_position": item[2],
                            "CDS_position": item[3],
                            "Protein_position": item[4],
                            "Amino_acids": item[5],
                            "Codons": item[6],
                            "Impact": item[7],
                            "Strand": item[8],
                            "HighestAF": str(item[9])
                        })
                    # print("------results ", results)

                except Exception as e:
                    print("Exception: ", e)
                    results = [{"Results": "No gene found or wrong input. Please check it again!"}]
                return results

# this is for API call
class GeneDetailBaseView(object):
    list_necessary_columns = [
        "Transcript_ID",
        "Consequence",
        "cDNA_position",
        "CDS_position",
        "Protein_position",
        "Amino_acids",
        "Codons",
        "Impact",
        "Strand",
        "BayesDel_addAF_rankscore",
        "BayesDel_noAF_rankscore",
        "CADD_raw_rankscore",
        "ClinPred_rankscore",
        "DANN_rankscore",
        "DEOGEN2_rankscore",
        "Eigen_PC_raw_coding_rankscore",
        "Eigen_raw_coding_rankscore",
        "FATHMM_converted_rankscore",
        "GERP_RS_rankscore",
        "GM12878_fitCons_rankscore",
        "GenoCanyon_rankscore",
        "H1_hESC_fitCons_rankscore",
        "HUVEC_fitCons_rankscore",
        "LIST_S2_rankscore",
        "LRT_converted_rankscore",
        "M_CAP_rankscore",
        "MPC_rankscore",
        "MVP_rankscore",
        "MetaLR_rankscore",
        "MetaRNN_rankscore",
        "MetaSVM_rankscore",
        "MutPred_rankscore",
        "MutationAssessor_rankscore",
        "MutationTaster_converted_rankscore",
        "PROVEAN_converted_rankscore",
        "Polyphen2_HDIV_rankscore",
        "Polyphen2_HVAR_rankscore",
        "PrimateAI_rankscore",
        "REVEL_rankscore",
        "SIFT4G_converted_rankscore",
        "SIFT_converted_rankscore",
        "SiPhy_29way_logOdds_rankscore",
        "VEST4_rankscore",
        "bStatistic_converted_rankscore",
        "Fathmm_MKL_coding_rankscore",
        "Fathmm_XF_coding_rankscore",
        "Integrated_fitCons_rankscore",
        "PhastCons30way_mammalian_rankscore",
        "PhyloP30way_mammalian_rankscore",
        "AM_pathogenicity",
        "HighestAF",
    ]

    browser_columns = ["Variant_marker"] + list_necessary_columns

    name_dic = {'NMD': 'NMD_transcript'
                , 'cse': 'coding_sequence'
                , 'fsh': 'frameshift',
                'itc': 'incomplete_terminal_codon'
                , 'ide': 'inframe_deletion'
                , 'iis': 'inframe_insertion',
                'mis': 'missense'
                , 'pal': 'protein_altering'
                , 'sac': 'splice_acceptor'
                , 'sdo': 'splice_donor',
                'sd5': 'splice_donor_5th_base'
                , 'sdr': 'splice_donor_region',
                'spt': 'splice_polypyrimidine_tract'
                , 'sre': 'splice_region'
                , '_sl': 'start_lost',
                '_sr': 'start_retained'
                , 'sga': 'stop_gained'
                , 'sl_': 'stop_lost'
                , 'sr_': 'stop_retained',
                'syn': 'synonymous'
                , 'H': 'high'
                , 'M': 'Medium'
                , 'L': 'Low'}

    def parse_marker_data(self, marker, vep_variant):

        # def is_primary_ts(ts):
        #     # Check if any row in the Gene model has the specified 'ts' in the 'primary_transcript' field
        #     exists = Gene.objects.filter(primary_transcript=ts).exists()
        #     if exists:
        #         return "YES"
        #     else:
        #         return "NO"

        data_subset = {}
        data_subset["Variant_marker"] = marker[0]
        data_subset["Transcript_ID"] = vep_variant[0]
        if vep_variant[1] in self.name_dic.keys():
            data_subset["Consequence"] = self.name_dic.get(vep_variant[1]).title()
        else:
            terms = vep_variant[1].split(",")
            data_subset["Consequence"] = ", ".join([self.name_dic.get(term).title() for term in terms])

        data_subset["cDNA_position"] = vep_variant[2]
        data_subset["CDS_position"] = vep_variant[3]
        data_subset["Protein_position"] = vep_variant[4]
        data_subset["Amino_acids"] = vep_variant[5]
        data_subset["Codons"] = vep_variant[6]
        data_subset["Impact"] = vep_variant[7]
        data_subset["Strand"] = vep_variant[8]
        data_subset["BayesDel_addAF_rankscore"] = vep_variant[9]
        data_subset["BayesDel_noAF_rankscore"] = vep_variant[10]
        data_subset["CADD_raw_rankscore"] = vep_variant[11]
        data_subset["ClinPred_rankscore"] = vep_variant[12]
        data_subset["DANN_rankscore"] = vep_variant[13]
        data_subset["DEOGEN2_rankscore"] = vep_variant[14]
        data_subset["Eigen_PC_raw_coding_rankscore"] = vep_variant[15]
        data_subset["Eigen_raw_coding_rankscore"] = vep_variant[16]
        data_subset["FATHMM_converted_rankscore"] = vep_variant[17]
        data_subset["GERP_RS_rankscore"] = vep_variant[18]
        data_subset["GM12878_fitCons_rankscore"] = vep_variant[19]
        data_subset["GenoCanyon_rankscore"] = vep_variant[20]
        data_subset["H1_hESC_fitCons_rankscore"] = vep_variant[21]
        data_subset["HUVEC_fitCons_rankscore"] = vep_variant[22]
        data_subset["LIST_S2_rankscore"] = vep_variant[23]
        data_subset["LRT_converted_rankscore"] = vep_variant[24]
        data_subset["M_CAP_rankscore"] = vep_variant[25]
        data_subset["MPC_rankscore"] = vep_variant[26]
        data_subset["MVP_rankscore"] = vep_variant[27]
        data_subset["MetaLR_rankscore"] = vep_variant[28]
        data_subset["MetaRNN_rankscore"] = vep_variant[29]
        data_subset["MetaSVM_rankscore"] = vep_variant[30]
        data_subset["MutPred_rankscore"] = vep_variant[31]
        data_subset["MutationAssessor_rankscore"] = vep_variant[32]
        data_subset["MutationTaster_converted_rankscore"] = vep_variant[33]
        data_subset["PROVEAN_converted_rankscore"] = vep_variant[34]
        data_subset["Polyphen2_HDIV_rankscore"] = vep_variant[35]
        data_subset["Polyphen2_HVAR_rankscore"] = vep_variant[36]
        data_subset["PrimateAI_rankscore"] = vep_variant[37]
        data_subset["REVEL_rankscore"] = vep_variant[38]
        data_subset["SIFT4G_converted_rankscore"] = vep_variant[39]
        data_subset["SIFT_converted_rankscore"] = vep_variant[40]
        data_subset["SiPhy_29way_logOdds_rankscore"] = vep_variant[41]
        data_subset["VEST4_rankscore"] = vep_variant[42]
        data_subset["bStatistic_converted_rankscore"] = vep_variant[43]
        data_subset["Fathmm_MKL_coding_rankscore"] = vep_variant[44]
        data_subset["Fathmm_XF_coding_rankscore"] = vep_variant[45]
        data_subset["Integrated_fitCons_rankscore"] = vep_variant[46]
        data_subset["PhastCons30way_mammalian_rankscore"] = vep_variant[47]
        data_subset["PhyloP30way_mammalian_rankscore"] = vep_variant[48]
        data_subset["AM_pathogenicity"] = vep_variant[49]
        data_subset["HighestAF"] = vep_variant[50]
        data_subset["primary"] = "YES"
        return data_subset

class GenebasedAssociationStatisticsView:
    def get_association_statistics_by_variant_marker(self, slug):
        context = {}
        if slug is not None:
            if cache.get("association_statistics_data_" + slug) is not None:
                table = cache.get("association_statistics_data_" + slug)
            else:
                table = pd.DataFrame()
                
                data = GenebassVariant.objects.filter(markerID_id=slug).values_list("markerID", "phenocode", "n_cases", "n_controls", "n_cases_defined", \
                                                                                "n_cases_both_sexes", "n_cases_females", "n_cases_males", "category", \
                                                                                "AC", "AF", "BETA", "SE", \
                                                                                "AF_Cases", "AF_Controls", "Pvalue")
                if len(data) == 0:
                    return dict()

                for row in data:
                    temp = pd.DataFrame([row])
                    phenocode = temp.iloc[0, 1]
                    temp.iloc[0, 1] = VariantPhenocode.objects.get(phenocode=phenocode).description_more
                    category = temp.iloc[0, 8]
                    temp.iloc[0, 8] = GenebassCategory.objects.get(category_code=category).category_description

                    table = table.append(temp, ignore_index=True)
                table.fillna('', inplace=True)
                table.columns=["markerID", "phenocode", "n_cases", "n_controls", "n_cases_defined", "n_cases_both_sexes", "n_cases_females", \
                                "n_cases_males", "category", "AC", "AF", "BETA", "SE", "AF_Cases", "AF_Controls", "Pvalue"]
                context = dict()
                cache.set("association_statistics_data_" + slug, table, 60 * 60)
            context['association_statistics_data'] = table
        return context

class DrugByGeneBaseView(object):
    def get_drug_by_gene_data(self, slug):
        context = {}
        if slug is not None:
            if cache.get("drug_data_" + slug) is not None:
                table = cache.get("drug_data_" + slug)
            else:
                table = pd.DataFrame()

                if slug.upper().startswith("ENSG"):
                    try:
                        protein = Protein.objects.get(geneID=slug)
                    except ObjectDoesNotExist:
                        print(f"No Protein found for geneID: {slug}")
                        protein = None
                else:
                    try:
                        protein = Protein.objects.get(genename=slug.upper())
                    except ObjectDoesNotExist:
                        protein = None
                if protein:
                    protein_ID = protein.uniprot_ID

                    drugs = Interaction.objects.filter(
                        uniprot_ID=protein_ID).values_list("drug_bankID", "actions", "known_action", "interaction_type")
                    for drug in drugs:
                        drug_df = pd.DataFrame([drug])
                        table = table.append(drug_df, ignore_index=True)
                    table.fillna('', inplace=True)
                    table.columns=["drug_bankID", "actions", "known_action", "interaction_type"]
                    context = dict()
                    cache.set("drug_data_" + slug, table, 60 * 60)
            context['list_of_targeting_drug'] = table
        return context

def parse_marker_data(marker, vep_variant): #lower, for one variant 
    # def is_primary_ts(ts):
    #     # Check if any row in the Gene model has the specified 'ts' in the 'primary_transcript' field
    #     exists = Gene.objects.filter(primary_transcript=ts).exists()
    #     if exists:
    #         return "YES"
    #     else:
    #         return "NO"

    data_subset = {}
    data_subset["Variant_marker"] = marker[0]
    data_subset["Transcript_ID"] = vep_variant[0]
    if vep_variant[1] in name_dic.keys():
        data_subset["Consequence"] = name_dic.get(vep_variant[1]).title()
    else:
        terms = vep_variant[1].split(",")
        data_subset["Consequence"] = ", ".join([name_dic.get(term).title() for term in terms])

    data_subset["cDNA_position"] = vep_variant[2]
    data_subset["CDS_position"] = vep_variant[3]
    data_subset["Protein_position"] = vep_variant[4]
    data_subset["Amino_acids"] = vep_variant[5]
    data_subset["Codons"] = vep_variant[6]
    data_subset["Impact"] = vep_variant[7]
    data_subset["Strand"] = "Reverse" if vep_variant[8] == -1 else "Forward"
    data_subset["BayesDel_addAF_rankscore"] = vep_variant[9]
    data_subset["BayesDel_noAF_rankscore"] = vep_variant[10]
    data_subset["CADD_raw_rankscore"] = vep_variant[11]
    data_subset["ClinPred_rankscore"] = vep_variant[12]
    data_subset["DANN_rankscore"] = vep_variant[13]
    data_subset["DEOGEN2_rankscore"] = vep_variant[14]
    data_subset["Eigen_PC_raw_coding_rankscore"] = vep_variant[15]
    data_subset["Eigen_raw_coding_rankscore"] = vep_variant[16]
    data_subset["FATHMM_converted_rankscore"] = vep_variant[17]
    data_subset["GERP_RS_rankscore"] = vep_variant[18]
    data_subset["GM12878_fitCons_rankscore"] = vep_variant[19]
    data_subset["GenoCanyon_rankscore"] = vep_variant[20]
    data_subset["H1_hESC_fitCons_rankscore"] = vep_variant[21]
    data_subset["HUVEC_fitCons_rankscore"] = vep_variant[22]
    data_subset["LIST_S2_rankscore"] = vep_variant[23]
    data_subset["LRT_converted_rankscore"] = vep_variant[24]
    data_subset["M_CAP_rankscore"] = vep_variant[25]
    data_subset["MPC_rankscore"] = vep_variant[26]
    data_subset["MVP_rankscore"] = vep_variant[27]
    data_subset["MetaLR_rankscore"] = vep_variant[28]
    data_subset["MetaRNN_rankscore"] = vep_variant[29]
    data_subset["MetaSVM_rankscore"] = vep_variant[30]
    data_subset["MutPred_rankscore"] = vep_variant[31]
    data_subset["MutationAssessor_rankscore"] = vep_variant[32]
    data_subset["MutationTaster_converted_rankscore"] = vep_variant[33]
    data_subset["PROVEAN_converted_rankscore"] = vep_variant[34]
    data_subset["Polyphen2_HDIV_rankscore"] = vep_variant[35]
    data_subset["Polyphen2_HVAR_rankscore"] = vep_variant[36]
    data_subset["PrimateAI_rankscore"] = vep_variant[37]
    data_subset["REVEL_rankscore"] = vep_variant[38]
    data_subset["SIFT4G_converted_rankscore"] = vep_variant[39]
    data_subset["SIFT_converted_rankscore"] = vep_variant[40]
    data_subset["SiPhy_29way_logOdds_rankscore"] = vep_variant[41]
    data_subset["VEST4_rankscore"] = vep_variant[42]
    data_subset["bStatistic_converted_rankscore"] = vep_variant[43]
    data_subset["Fathmm_MKL_coding_rankscore"] = vep_variant[44]
    data_subset["Fathmm_XF_coding_rankscore"] = vep_variant[45]
    data_subset["Integrated_fitCons_rankscore"] = vep_variant[46]
    data_subset["PhastCons30way_mammalian_rankscore"] = vep_variant[47]
    data_subset["PhyloP30way_mammalian_rankscore"] = vep_variant[48]
    data_subset["AM_pathogenicity"] = vep_variant[49]
    data_subset["HighestAF"] = vep_variant[50]
    data_subset["primary"] = "YES"
    return data_subset

def get_variant_annotation_and_vep(request, slug): #lower for one gene
    context = {}
    if slug is not None:
        if cache.get("variant_annotation_and_vep_data_" + slug) is not None:
            context = cache.get("variant_annotation_and_vep_data_" + slug)
        else:
            table = pd.DataFrame(columns=browser_columns)
            geneid = ""
            if slug.startswith("ENSG"):
                marker_ID_data = Variant.objects.filter(Gene_ID=slug).values_list(
                    "VariantMarker")
                geneid = slug
            else:
                geneid = Gene.objects.filter(genename=slug).values_list("gene_id")[0][0]
                marker_ID_data = Variant.objects.filter(Gene_ID=geneid).values_list(
                    "VariantMarker")
            objs = Gene.objects.filter(gene_id=geneid).values_list("primary_transcript", flat=True)
            if objs:
                pt = objs[0] #take the primary_transcript
                for marker in marker_ID_data:
                    # Retrieve all VEP variants for each variant marker
                    vep_variants = VepVariant.objects.filter(
                        Q(Variant_marker=marker)&Q(Transcript_ID=pt)).exclude(Protein_position__icontains='-').values_list(
                        *list_necessary_columns)
                    for vep_variant in vep_variants:
                        data_subset = parse_marker_data(marker, vep_variant)
                        table = table.append(data_subset, ignore_index=True)
            table.fillna('', inplace=True)
            table_with_mean_vep_score = []
            for i, data_row in enumerate(table.to_numpy()):
                try:
                    # cleaned_values = [x for x in data_row[10:-2] if str(x) != '']
                    cleaned_values = [x for x in data_row[10:-2] if x is not None and str(x) != '']

                    mean_vep_score = round(np.mean(cleaned_values), 3)
                    if np.isnan(mean_vep_score):
                        mean_vep_score = "nan"

                    std_vep_score = round(np.std(cleaned_values, ddof=1), 3)
                    if np.isnan(std_vep_score):
                        std_vep_score = "nan"

                    data_row = np.append(data_row, mean_vep_score)
                    data_row = np.append(data_row, std_vep_score)
                    table_with_mean_vep_score.append(data_row)
                    
                except Exception as e:
                    print("Exception ", e)
            # print("table_with_mean_vep_score length ", len(table_with_mean_vep_score))
            table_with_protein_pos_int = []
            fields = list(table.columns)
            fields.append("Mean_VEP_score")
            fields.append("Std_VEP_score")
            number_of_fields = len(fields)
            for data_row in table_with_mean_vep_score:
                try:
                    data_row[5] = int(data_row[5])  # protein position
                    temp=[]
                    for i in range(number_of_fields):
                        temp.append(data_row[i])
                    table_with_protein_pos_int.append(temp)
                except Exception as e:
                    pass
            context['array'] = table_with_protein_pos_int
            cache.set("variant_annotation_and_vep_data_" + slug, context, 60 * 60)
            print("len of table_with_protein_pos_int ", len(table_with_protein_pos_int))
            print("len of table_with_protein_pos_int element ", len(table_with_protein_pos_int[0]))
    return JsonResponse(context, safe=False)

# Function to remove duplicates in a list of dictionary
def remove_duplicates(dict_list):
    seen = set()
    unique_list = []
    for d in dict_list:
        # Convert dictionary to a tuple of its items
        t = tuple(d.items())
        if t not in seen:
            seen.add(t)
            unique_list.append(d)
    return unique_list

def get_gene_detail_data(request, slug): #upper
    context = {}
    if slug is not None:
        if cache.get("gene_detail_data_" + slug) is not None:
            context = cache.get("gene_detail_data_" + slug)
        else:
            geneid = ""
            context = dict()
            variant_info_for_3D = []
            protein_with_variant_index_list=[] 
            if slug.startswith("ENSG"):
                print("slug startswith ENSG slug = ",slug) 
                marker_ID_data = list(set(Variant.objects.filter(Gene_ID=slug).values_list(
                    "VariantMarker", flat=True)))
                geneid = slug
            else:
                geneid = Gene.objects.filter(genename=slug).values_list("gene_id")[0][0]
                marker_ID_data = list(set(Variant.objects.filter(Gene_ID=geneid).values_list(
                    "VariantMarker", flat=True)))
                print("length marker_ID_data ", len(marker_ID_data))
            objs = Gene.objects.filter(gene_id=geneid).values_list("primary_transcript", flat=True)
            protein_position_and_corresponding_lowest_mean_VEP_score = {}
            
            if objs:
                pt = objs[0] #take the primary_transcript
                print("primary transcript = ", pt)
                for marker in marker_ID_data:
                    vep_variants = VepVariant.objects.filter(
                        Q(Variant_marker=marker)&Q(Transcript_ID=pt)).exclude(Protein_position__icontains='-').values_list(*list_necessary_columns_2
                        )
                    try:
                        for vep_variant in vep_variants:
                            if (vep_variant[2]=="2"):
                                print("positiion 2, ")
                            coseq = vep_variant[1].split(",")
                            cleaned_values = [x for x in vep_variant[6:] if isinstance(x, float) and not np.isnan(x)]
                            mean_vep_score = round(np.mean(cleaned_values), 3)
                            if np.isnan(mean_vep_score):
                                mean_vep_score = "nan"
                            # one protein postion may have more than one variants --> more than one MVS
                            protein_position_and_corresponding_lowest_mean_VEP_score.setdefault(vep_variant[2], []).append(mean_vep_score)
                            consequences=[]
                            if len(coseq) >= 1:
                                for c in coseq:
                                    consequences.append(name_dic.get(c).title())
                            if vep_variant[3].find("/")>0:
                                wtaa = vep_variant[3].split("/")[0]
                                mtaa = vep_variant[3].split("/")[1]
                            else:
                                wtaa = vep_variant[3]
                                mtaa = vep_variant[3]
                            if (vep_variant[2]=="2"):
                                print("******------ positiion 2, wtaa:", wtaa, " mtaa:", mtaa, "vep score:")
                                for v in vep_variant[6:]:
                                    print(type(v))
                            temp = {
                                    "geneID": geneid,
                                    "variant_marker": marker,
                                    "consequence": ", ".join(list(set(consequences))),
                                    "protein_position": vep_variant[2],
                                    "wtaa": wtaa, #wildtype AA
                                    "mtaa": mtaa, #mutant AA
                                    "codon": vep_variant[4],
                                    "HighestAF": str(vep_variant[5]),
                                    "Mean_VEP_Score": mean_vep_score,
                                    }
                            variant_info_for_3D.append(temp)
                            protein_with_variant_index_list.append(vep_variant[2])
                    except Exception as e:
                        print("----- marker ", marker, " has exception ", e)
                        raise
            variant_info_for_3D = remove_duplicates(variant_info_for_3D)
            variant_info_for_3D_view = sorted(variant_info_for_3D, key=lambda x: int(x['protein_position']))
            # print("*********---------- variant_info_for_3D_view after remove dup and sort ", variant_info_for_3D_view[:10])
            context['variant_info_for_3D_view'] = json.dumps(variant_info_for_3D_view)
            context['protein_with_variant_index_list'] = protein_with_variant_index_list
            # print("---- VIEW function: protein_with_variant_index_list: ", protein_with_variant_index_list)
            context['genename'] = Gene.objects.filter(gene_id=slug).values_list("genename", flat=True)[0]
            context['geneID'] = slug
            amino_seq = Protein.objects.filter(geneID=slug).values_list("sequence", flat=True)[0]
            amino_seq_num_list = list(range(1, len(amino_seq) + 1))
            context["amino_seq"] = amino_seq
            context["seq_length"] = len(amino_seq)
            protein_name = Protein.objects.filter(geneID=slug).values_list("uniprot_ID", flat=True)[0]
            context["protein_name"] = protein_name
            protein_text_name = Protein.objects.filter(geneID=slug).values_list("protein_name", flat=True)[0]
            context["protein_text_name"] = protein_text_name
            context["amino_seq_num_list"] = amino_seq_num_list
            new_dict = {}
            for key, values in protein_position_and_corresponding_lowest_mean_VEP_score.items():
                numeric_values = [float(v) for v in values if v != 'nan']
                if numeric_values:
                    new_dict[key] = min(numeric_values)
                else:
                    new_dict[key] = 'nan'
            
            chunks = []
            for i in range(0, len(amino_seq), 10):
                t = []
                for k in range(1, 11):
                    aa = amino_seq[i+k-1:i+k]
                    score = new_dict.get(str(i+k), "no variants")
                    n = protein_position_and_corresponding_lowest_mean_VEP_score.get(str(i+k))
                    if not(n):
                        no_of_variants_at_aa = 0
                    else:
                        no_of_variants_at_aa = len(n)
                    t.append([aa, k, score, no_of_variants_at_aa])
                
                chunks.append({
                            "aa_and_index_and_score":t,
                            "position": i + 10
                    })
            chunks[-1]["position"] = 10 + int(len(amino_seq)/10)*10
            context["chunks"] = chunks
            
            context["af_pdb"] = Protein.objects.filter(geneID=slug).values_list("af_pdb", flat=True)[0]
            variants = [item["variant_marker"] for item in variant_info_for_3D_view]
            context['variants'] = list(set(variants))
            cache.set("gene_detail_data_" + slug, context, 60 * 60)
    return render(request, 'gene_detail.html', context)


def get_protein_position_of_variant(request):
    gene_id = request.GET.get("gene_id")
    primary_transcript = gene.objects.get(gene_id=gene_id)
    protein_position = VepVariant.objects.filter(Transcript_ID=primary_transcript).values_list("Variant_marker", "Protein_position", "HighestAF")



@require_http_methods(["GET"])
def filter_gene_detail_page(request, id):
    mean_vep_score = request.GET.get('mean_vep_score', 0.5)
    mean_vep_score = float(mean_vep_score)
    # Filter by mean_vep_score
    list_vep_variants = VepVariant.objects.filter(
        Variant_marker__in=Variant.objects.filter(Gene_ID=id).values_list('VariantMarker',
                                                                          flat=True)
        ).exclude(Protein_position__contains="-").annotate(
        protein_pos_int=Cast('Protein_position', IntegerField()),
        mean_vep_score=(F('BayesDel_addAF_rankscore') + F('BayesDel_noAF_rankscore')) / 2
    ).filter(mean_vep_score__gte=mean_vep_score).exclude(mean_vep_score=decimal.Decimal('NaN')).order_by(
        'protein_pos_int')

    return None


@require_http_methods(["GET"])
def genebass_variants(request):
    """
    Return a list of genebass variants by variant_id
    """
    variant_id = request.GET.get('variant_id', None)
    if variant_id:
        pass
        # TODO: Filter genebass variants by variant_id
    else:
        return HttpResponseBadRequest()


### API
class GeneDetailApiView(
    View,
    GeneDetailBaseView,
):

    def get(self, request, *args, **kwargs):
        """
        Return a list of genebass variants by variant_id
        """
        gene_id = self.kwargs.get('gene_id', None)
        data = self.get_gene_detail_data(gene_id)

        # Convert np.array to list to make it JSON serializable
        array = data['array']
        array_in_list = []
        for item in array:
            array_in_list.append(item.tolist())
        data['array'] = array_in_list

        return JsonResponse(data, safe=False)