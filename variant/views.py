from django.http import HttpResponse, JsonResponse
from django.template.loader import render_to_string
from django.core.cache import cache
from django.shortcuts import render
import numpy as np
import json
import math
from .models import (
    GenebassVariant,
    Variant,
    VepVariant,
)
from rest_framework import generics
from .serializers import VepVariantSerializer
from django.db.models import Q

class VepVariantListView(generics.ListAPIView):
    serializer_class = VepVariantSerializer
    def get_queryset(self):
        # Retrieve the gene_id from the URL parameter
        gene_id = self.kwargs['gene_id']
        # Filter VepVariant objects based on the gene_id
        queryset = VepVariant.objects.filter(Variant_marker__Gene_ID__gene_id=gene_id)
        return queryset

#get VEP from a variant marker
class VEPFromVariantBaseView:
    def get_vep_from_variant(self, slug):
        context = {}
        slug = slug[:-1] if slug[-1] == "/" else slug
        
        if slug is not None:
            if cache.get("vep_by_variant_marker_" + slug) is not None:
                returned_data = cache.get("vep_by_variant_marker_" + slug)
            else:
                vep_rows = VepVariant.objects.filter(Variant_marker=slug)
                returned_data = []
                for r in vep_rows:
                    row = {
                            "Transcript_ID": str(r.Transcript_ID),
                            "AM_pathogenicity": str(r.AM_pathogenicity),
                            "BayesDel_addAF_rankscore": str(r.BayesDel_addAF_rankscore),
                            "BayesDel_noAF_rankscore": str(r.BayesDel_noAF_rankscore),
                            "CADD_raw_rankscore": str(r.CADD_raw_rankscore),
                            "ClinPred_rankscore": str(r.ClinPred_rankscore),
                            "DANN_rankscore": str(r.DANN_rankscore),
                            "DEOGEN2_rankscore": str(r.DEOGEN2_rankscore),
                            "Eigen_PC_raw_coding_rankscore": str(r.Eigen_PC_raw_coding_rankscore),
                            "Eigen_raw_coding_rankscore": str(r.Eigen_raw_coding_rankscore),
                            "FATHMM_converted_rankscore": str(r.FATHMM_converted_rankscore),
                            "GERP_RS_rankscore": str(r.GERP_RS_rankscore),
                            "GM12878_fitCons_rankscore": str(r.GM12878_fitCons_rankscore),
                            "GenoCanyon_rankscore": str(r.GenoCanyon_rankscore),
                            "H1_hESC_fitCons_rankscore": str(r.H1_hESC_fitCons_rankscore),
                            "HUVEC_fitCons_rankscore": str(r.HUVEC_fitCons_rankscore),
                            "LIST_S2_rankscore": str(r.LIST_S2_rankscore),
                            "LRT_converted_rankscore": str(r.LRT_converted_rankscore),
                            "M_CAP_rankscore": str(r.M_CAP_rankscore),
                            "MPC_rankscore": str(r.MPC_rankscore),
                            "MVP_rankscore": str(r.MVP_rankscore),
                            "MetaLR_rankscore": str(r.MetaLR_rankscore),
                            "MetaRNN_rankscore": str(r.MetaRNN_rankscore),
                            "MetaSVM_rankscore": str(r.MetaSVM_rankscore),
                            "MutPred_rankscore": str(r.MutPred_rankscore),
                            "MutationAssessor_rankscore": str(r.MutationAssessor_rankscore),
                            "MutationTaster_converted_rankscore": str(r.MutationTaster_converted_rankscore),
                            "PROVEAN_converted_rankscore": str(r.PROVEAN_converted_rankscore),
                            "Polyphen2_HDIV_rankscore": str(r.Polyphen2_HDIV_rankscore),
                            "Polyphen2_HVAR_rankscore": str(r.Polyphen2_HVAR_rankscore),
                            "PrimateAI_rankscore": str(r.PrimateAI_rankscore),
                            "REVEL_rankscore": str(r.REVEL_rankscore),
                            "SIFT4G_converted_rankscore": str(r.SIFT4G_converted_rankscore),
                            "SIFT_converted_rankscore": str(r.SIFT_converted_rankscore),
                            "SiPhy_29way_logOdds_rankscore": str(r.SiPhy_29way_logOdds_rankscore),
                            "VEST4_rankscore": str(r.VEST4_rankscore),
                            "bStatistic_converted_rankscore": str(r.bStatistic_converted_rankscore),
                            "Fathmm_MKL_coding_rankscore": str(r.Fathmm_MKL_coding_rankscore),
                            "Fathmm_XF_coding_rankscore": str(r.Fathmm_XF_coding_rankscore),
                            "Integrated_fitCons_rankscore": str(r.Integrated_fitCons_rankscore),
                            "PhastCons30way_mammalian_rankscore": str(r.PhastCons30way_mammalian_rankscore),
                            "PhyloP30way_mammalian_rankscore": str(r.PhyloP30way_mammalian_rankscore),
                            "LINSIGHT_rankscore": str(r.LINSIGHT_rankscore),
                         }
                    returned_data.append(row)
                context = dict()
                cache.set("vep_by_variant_marker_" + slug, returned_data, 60 * 60)
            context['vep'] = returned_data
        return context

list_of_score_names = ["BayesDel_addAF_rankscore",
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
                        "LINSIGHT_rankscore"]
    
def get_variant_vep_scores_and_plot(request):
    """
        Get the vep scores for a specific variant
    """
    variant_maker_list = request.GET.get("variant_maker_list").split(',')
    variant_maker_list_data = []

    # Get variant
    for variant_marker in variant_maker_list:
        try:
            variant = Variant.objects.get(VariantMarker=variant_marker) # primary key
        except Variant.DoesNotExist:
            variant = None

        # Get primary transcript
        if variant:
            prrimary_ts = variant.Gene_ID.primary_transcript
        else:
            prrimary_ts = None

        temp = VepVariant.objects.filter(Q(Variant_marker=variant_marker)&Q(Transcript_ID=prrimary_ts)).values('Amino_acids', 'Protein_position').first()
        if temp["Amino_acids"].find("/")<0:
            category2 = temp["Amino_acids"]+temp["Protein_position"]+temp["Amino_acids"]
        else:
            category2 = temp["Amino_acids"].split("/")[0]+temp["Protein_position"]+temp["Amino_acids"].split("/")[1]
        list_vep_scores = VepVariant.objects.filter(Q(Variant_marker=variant_marker)&Q(Transcript_ID=prrimary_ts)).values(
                        *list_of_score_names).first()
        if list_vep_scores:
            list_vep_scores = list(list_vep_scores.values())
        else:
            list_vep_scores = []

        # Remove NaN values
        list_vep_scores = list(filter(lambda value: not math.isnan(value), list_vep_scores))
        variant_maker_list_data.append({"category":variant_marker, "category2":category2, "values": list_vep_scores})
    
    return JsonResponse(
        {
            "variant_maker_list_data": variant_maker_list_data,
        }
    )


def get_genebass_tables(request):
    """
        Get the genebass tables for a variant.
    """
    variant_marker = request.GET.get("variant_marker")
    # Get variant
    try:
        variant = Variant.objects.filter(VariantMarker=variant_marker).first()
    except Variant.DoesNotExist:
        variant = None

    print("------ get_genebass_tables is call for variant ", variant)

    # Get gene
    if variant:
        gene = variant.Gene_ID
        primary_transcript = variant.Gene_ID.primary_transcript
        gene_id= variant.Gene_ID.gene_id
    else:
        gene = None
        primary_transcript = None
        gene_id = None

    # Get transcript
    transcript_ids = list(set(VepVariant.objects.filter(Variant_marker=variant_marker).values_list('Transcript_ID', flat=True)))
    try:
        transcript_ids.remove(primary_transcript)
    except ValueError:
        pass  # Do nothing if primary_transcript is not in the list

    list_genebass = GenebassVariant.objects.filter(markerID=variant_marker).values(
        'n_cases',
        'n_controls',
        'phenocode__description',
        'phenocode',
        # 'n_cases_defined',
        # 'n_cases_both_sexes',
        # 'n_cases_females',
        # 'n_cases_males',
        'category__category_description',
        'AC',
        'AF',
        'BETA',
        'SE',
        'AF_Cases',
        'AF_Controls',
        'Pvalue',
    )

    if list_genebass.count() > 0:
        context = {
            "gene": gene,
            "list_genebass": list_genebass,
            "transcript_ids": transcript_ids,
            "primary_transcript": primary_transcript,
            "variant": variant,
            "gene_id": gene_id,
                }
    else:
        context = {
            "gene": gene,
            "list_genebass": None,  # or keep it as an empty list, depending on your template logic
            "transcript_ids": transcript_ids,
            "primary_transcript": primary_transcript,
            "variant": variant,
            "gene_id": gene_id,
        }

    html = render_to_string(
        template_name="variant/genebass_tables.html",
        context=context,
        request=request,
    )
    print("---- context ", context)

    return HttpResponse(html)

