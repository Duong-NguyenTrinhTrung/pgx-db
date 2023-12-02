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


warnings.filterwarnings('ignore')

class GenebasedAssociationStatisticsView:
    def get_association_statistics_by_variant_marker(self, slug):
        context = {}
        print("get_association_statistics_by_variant_marker: slug: ", slug)
        if slug is not None:
            print("cached:", cache.__dict__)
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
                        print("geneID:", slug)
                        protein = Protein.objects.get(genename=slug.upper())
                        print("Data query geneID: ", protein.__dict__)
                    except ObjectDoesNotExist:
                        print(f"No Protein found for genename: {slug}")
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

class GeneDetailBaseView(object):
    browser_columns = [
        "Variant_marker",  # MarkerID
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
    ]

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
    ]

    name_dic = {'NMD': 'NMD_transcript', 'cse': 'coding_sequence', 'fsh': 'frameshift',
                'itc': 'incomplete_terminal_codon', 'ide': 'inframe_deletion', 'iis': 'inframe_insertion',
                'mis': 'missense', 'pal': 'protein_altering', 'sac': 'splice_acceptor', 'sdo': 'splice_donor',
                'sd5': 'splice_donor_5th_base', 'sdr': 'splice_donor_region',
                'spt': 'splice_polypyrimidine_tract', 'sre': 'splice_region', '_sl': 'start_lost',
                '_sr': 'start_retained', 'sga': 'stop_gained', 'sl_': 'stop_lost', 'sr_': 'stop_retained',
                'syn': 'synonymous', 'H': 'high', 'M': 'Medium', 'L': 'Low'}

    def parse_marker_data(self, marker, vep_variant):

        def is_primary_ts(ts):
            # Check if any row in the Gene model has the specified 'ts' in the 'primary_transcript' field
            exists = Gene.objects.filter(primary_transcript=ts).exists()
            if exists:
                return "YES"
            else:
                return "NO"

        data_subset = {}
        data_subset["Variant_marker"] = marker[0]
        data_subset["Transcript_ID"] = vep_variant[0]
        if vep_variant[1] in self.name_dic.keys():
            data_subset["Consequence"] = self.name_dic.get(vep_variant[1]).title()
        else:
            data_subset["Consequence"] = "Re-check"

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
        data_subset["primary"] = is_primary_ts(vep_variant[0])

        return data_subset

    def get_gene_detail_data(self, slug):

        context = {}
        if slug is not None:
            if cache.get("variant_data_" + slug) is not None:
                table_with_protein_pos_int = cache.get("variant_data_" + slug)
            else:
                browser_columns = self.browser_columns

                table = pd.DataFrame(columns=browser_columns)

                # Retrieve all variant markers from a gene
                if slug.startswith("ENSG"):
                    marker_ID_data = Variant.objects.filter(Gene_ID=slug).values_list(
                        "VariantMarker")
                else:
                    geneid = Gene.objects.filter(genename=slug).values_list("gene_id")[0][0]
                    marker_ID_data = Variant.objects.filter(Gene_ID=geneid).values_list(
                        "VariantMarker")

                # Below code should be rewritten to avoid N+1 queries
                for marker in marker_ID_data:
                    # Retrieve all VEP variants for each variant marker
                    vep_variants = VepVariant.objects.filter(
                        # *: passing every element of a list to values_list rather than passing a list as one argument
                        Variant_marker=marker).exclude(Protein_position__icontains='-').values_list(
                        *self.list_necessary_columns)
                    for vep_variant in vep_variants:
                        data_subset = self.parse_marker_data(marker, vep_variant)
                        table = table.append(data_subset, ignore_index=True)

                table.fillna('', inplace=True)

                context = dict()

                table_with_mean_vep_score = []
                table_index = 0
                cleaned_value_index = 0
                for data_row in table.to_numpy():
                    table_index += 1
                    try:
                        cleaned_values = [x for x in data_row[10:-1] if str(x) != '']
                        if len(cleaned_values) != 0:
                            cleaned_value_index += 1
                            mean_vep_score = round(np.mean(cleaned_values), 2)
                            table_with_mean_vep_score.append(np.append(data_row, mean_vep_score))
                    except Exception as e:
                        pass

                table_with_protein_pos_int = []
                for data_row in table_with_mean_vep_score:
                    try:
                        data_row[5] = int(data_row[5])  # protein position
                        table_with_protein_pos_int.append(data_row)
                    except Exception as e:
                        pass

                cache.set("variant_data_" + slug, table_with_protein_pos_int, 60 * 60)
            context['array'] = table_with_protein_pos_int
            context['length'] = len(table_with_protein_pos_int)
            context["name_dic"] = self.name_dic

            # Mean of Vep scores form
            context['gene'] = Gene.objects.filter(gene_id=slug).values_list("genename", flat=True)[0]
            context['geneID'] = slug
            amino_seq = Protein.objects.filter(geneID=slug).values_list("sequence", flat=True)[0]
            amino_seq_num_list = list(range(1, len(amino_seq) + 1))
            context["amino_seq"] = amino_seq
            context["seq_length"] = len(amino_seq)
            protein_name = Protein.objects.filter(geneID=slug).values_list("uniprot_ID", flat=True)[0]
            context["protein_name"] = protein_name
            context["amino_seq_num_list"] = amino_seq_num_list
            chunks = [{"chunk": amino_seq[i:i + 10], "position": i + 10} for i in range(0, len(amino_seq), 10)]
            chunks[-1]["position"] = len(amino_seq)
            context["chunks"] = chunks
            context["af_pdb"] = Protein.objects.filter(geneID=slug).values_list("af_pdb", flat=True)[0]

            transcripts = [item[1] for item in table_with_protein_pos_int]
            context['transcripts'] = list(set(transcripts))
            variants = [item[0] for item in table_with_protein_pos_int]
            context['variants'] = list(set(variants))

            consequences = []
            for item in table_with_protein_pos_int:
                coseq = item[2].split(",")
                if len(coseq) >= 1:
                    consequences += coseq

            context['consequences'] = list(set(consequences))

        return context


class GeneDetailBrowser(
    GeneDetailBaseView,
    TemplateView,
):
    template_name = 'gene_detail.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        slug = kwargs.get('slug')
        context.update(self.get_gene_detail_data(slug))
        return context


class GenebassVariantListView(TemplateView):
    template_name = "genebass/variant_list.html"

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)

        genebass_variants_list = GenebassVariant.objects.filter(  # Filter to get all genebass variants for a gene
            markerID__in=Variant.objects.filter(  # Filter to get all variants for a gene
                Gene_ID=self.kwargs['pk']  # Gen Gene by gene_id
            ).values_list('VariantMarker', flat=True)
        ).values(
            'n_cases',
            'n_controls',
            'phenocode__description',
            'phenocode',
            'n_cases_defined',
            'n_cases_both_sexes',
            'n_cases_females',
            'n_cases_males',
            'category',
            'AC',
            'AF',
            'BETA',
            'SE',
            'AF_Cases',
            'AF_Controls',
            'Pvalue',
        )

        genebass_variants_list = genebass_variants_list[:5000]

        phenotypes = GenebassVariant.objects.filter(  # Filter to get all genebass variants for a gene
            markerID__in=Variant.objects.filter(  # Filter to get all variants for a gene
                Gene_ID=self.kwargs['pk']  # Gen Gene by gene_id
            ).values_list('VariantMarker', flat=True)
        ).values_list('phenocode', flat=True).distinct()

        # change query to take categories
        categories = GenebassVariant.objects.filter(  # Filter to get all genebass variants for a gene
            markerID__in=Variant.objects.filter(  # Filter to get all variants for a gene
                Gene_ID=self.kwargs['pk']  # Gen Gene by gene_id
            ).values_list('VariantMarker', flat=True)
        ).values_list('category', flat=True).distinct()

        context['gene'] = Gene.objects.get(pk=self.kwargs['pk'])
        context['variant_list'] = genebass_variants_list
        context['phenotypes'] = phenotypes
        context['categories'] = categories

        return context


@require_http_methods(["GET"])
def filter_gene_detail_page(request, id):
    """
    Filter gene detail page by
    * mean_of_vep_score
    """
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
