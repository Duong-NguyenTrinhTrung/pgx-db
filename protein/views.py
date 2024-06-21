import hashlib
import itertools
import json
import re
import time
import pandas as pd
import urllib

from random import SystemRandom
from copy import deepcopy
from collections import defaultdict, OrderedDict

from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.views.generic import TemplateView, DetailView

from django.db.models import Q, Count, Subquery, OuterRef
from django.views.decorators.csrf import csrf_exempt

from django.core.cache import cache
from protein.models import Protein
from django.shortcuts import render
import py3Dmol
from py3Dmol import view
from interaction.models import Interaction
from drug.models import Drug, DrugAtcAssociation
from disease.models import Disease, DrugDiseaseStudy
from variant.models import GenebassPGx, GenebassVariantPGx, Pharmgkb
from gene.models import Gene 



# from common.views import AbsBrowseSelection
# class BrowseSelection(AbsBrowseSelection):
#     title = 'SELECT A RECEPTOR (FAMILY)'
#     description = 'Select a target or family by searching or browsing in the right column.'
#     description = 'Select a receptor (family) by searching or browsing in the middle. The selection is viewed to' \
#                   + ' the right.'
#     docs = 'receptors.html'
#     target_input=False


class BundleByTargetCodeView:
    def get_bundle_data_by_target(self, slug):
        context = {}
        if slug is not None:
            if cache.get("get_bundle_data_by_target_" + slug) is not None:
                returned_data = cache.get("get_bundle_data_by_target_" + slug)
            else:
                gene_id = Protein.objects.get(uniprot_ID=slug).geneID
                genename = Protein.objects.get(uniprot_ID=slug).genename
                drugs = list(Interaction.objects.filter(
                        uniprot_ID__uniprot_ID=slug).values_list("drug_bankID", flat=True))
                total_gb_pgx = GenebassPGx.objects.filter(drugbank_id__in=drugs, gene_id=gene_id, Pvalue__lte=0.05).count()
                total_ph_pgx = Pharmgkb.objects.filter(drugbank_id__in=drugs,geneid=gene_id,P_Value__isnull=False,P_Value_numeric__lte=0.05).count()
                total_studies = DrugDiseaseStudy.objects.filter(drug_bankID__in=drugs).count()
                
                rows = []
                for drug in drugs:
                    list_of_atc_codes = list(DrugAtcAssociation.objects.filter(
                        drug_id=drug).values_list("atc_id", flat=True))
                    mode_of_actions = list(Interaction.objects.filter(
                        Q(drug_bankID=drug)&Q(uniprot_ID__uniprot_ID=slug)).values_list("interaction_type", flat=True))
                    drug_action = list(Interaction.objects.filter(Q(drug_bankID=drug)&Q(uniprot_ID__uniprot_ID=slug)).values_list("actions", flat=True))
                    
                    gb_pgx = GenebassPGx.objects.filter(
                        drugbank_id=drug,
                        gene_id=gene_id,
                        Pvalue__lte=0.05,
                        # annotation="pLoF",
                    )
                    ph_pgx = Pharmgkb.objects.filter(
                        drugbank_id=drug,
                        geneid=gene_id,
                        P_Value__isnull=False,
                        # P_Value__startswith="=",
                        P_Value_numeric__lte=0.05
                    )
                    studies = DrugDiseaseStudy.objects.filter(drug_bankID=drug)
                    no_of_indications = DrugDiseaseStudy.objects.filter(Q(drug_bankID=drug)&Q(clinical_trial=4)).count()
                    no_of_phase3 = DrugDiseaseStudy.objects.filter(Q(drug_bankID=drug)&Q(clinical_trial=3)).count()
                    study_data = []
                    for study in studies:
                        temp = {
                            
                            "disease_name" : study.disease_name.disease_name,
                            "trial_phase" : study.clinical_trial,
                            "disease_class" : study.disease_name.disease_class,
                        }
                        study_data.append(temp)
                    row = {
                            "drug": drug,
                            "Atc_code" : ",".join(list_of_atc_codes),
                            "mode_of_action" : ",".join(mode_of_actions),
                            "drug_action" : ",".join(drug_action),
                            "no.OfStudies": studies.count(),
                            "no.OfIndications": no_of_indications,
                            "no.OfClinicalTrialPhase3": no_of_phase3,
                            "genebassPGxCount" : gb_pgx.count(),
                            "pharmgKbPGxCount" : ph_pgx.count(),
                            "study_data": study_data,
                    }
                    rows.append(row)
                returned_data = {
                    "No. of drug_protein interactions": len(drugs),
                    "Total number of genebass burden associations": total_gb_pgx,
                    "Total number of PharmgKB associations": total_ph_pgx,
                    "Total number of drug_disease association studies": total_studies,
                    "Details": rows,
                }
                cache.set("get_bundle_data_by_target_" + slug, returned_data, 60 * 60)
            context['Bundle data for target '+ slug +" ("+genename+")"] = returned_data
        return context


# Create your views here.
def protein_view_ex(request):
    # Generate a protein structure using py3Dmol
    pdb_str = 'ATOM      1  N   GLY A   1      -0.364   0.600   0.000  1.00  0.00           N  '
    v = view(width=600, height=400)
    v.addModel(pdb_str, 'pdb')
    v.setStyle({'cartoon': {'color': 'spectrum'}})
    v.zoomTo()
    v.setBackgroundColor('0xeeeeee')
    # Return the HTML and JavaScript code for the py3Dmol viewer
    return render(request, 'protein_3Dview_ex.html', {'viewer': v.js()})

# class ProteinBrowser(TemplateView):

#     template_name = 'protein_browser.html'
#     def get_context_data(self, **kwargs):
#         context = super().get_context_data(**kwargs)
#         browser_columns = ["uniprot_ID", "genename",
#                            "geneID", "protein_name"]
#         table = pd.DataFrame(columns=browser_columns)
#         protein_data = Protein.objects.all().values_list(
#             "uniprot_ID",
#             "genename",
#             "geneID",
#             "protein_name"
#         ).distinct()
#         for data in protein_data:
#             data_subset = {}
#             data_subset['uniprot_ID'] = data[0]
#             data_subset['genename'] = data[1]
#             data_subset['geneID'] = data[2]
#             data_subset['protein_name'] = data[3]

#             table = table.append(data_subset, ignore_index=True)

#         table.fillna('', inplace=True)
#         # context = dict()
#         context['Array'] = table.to_numpy()
#         return context

#@cache_page(60 * 60 * 24 * 7)
def get_protein_details(request, slug):
    # get protein
    slug = slug.upper()

    try:
        if Protein.objects.filter(uniprot_ID=slug).exists():
            p = Protein.objects.get(uniprot_ID=slug)
        
    except:
        context = {'protein_no_found': slug}
        return render(request, 'protein_detail.html', context)

    # context_list=[]
    # for p in ps:

    # get family list
    uniprot_id = p.uniprot_ID
    protein_name = p.protein_name

    context = {'uniprot_ID': uniprot_id, 'protein_name': protein_name}
    return render(request, 'protein_detail.html', context)