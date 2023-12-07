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
from variant.models import Variant
from interaction.models import Interaction
from gene.models import Gene
from drug.models import Drug, DrugAtcAssociation
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist


def protein_autocomplete_view(request):
    query = request.GET.get('query', '')
    proteins = Protein.objects.filter(Q(uniprot_ID__icontains=query) | Q(protein_name__icontains=query) | Q(geneID__icontains=query) | Q(genename__icontains=query))
    result_uniprot_ID = Protein.objects.filter(uniprot_ID__icontains=query)
    
    if len(result_uniprot_ID) == 0:
        result_protein_name = Protein.objects.filter(protein_name__icontains=query)
        if len(result_protein_name) == 0:
            result_geneID = Protein.objects.filter(geneID__icontains=query)
            if len(result_geneID) == 0:
                result_genename = Protein.objects.filter(genename__icontains=query)
                results = [protein.genename for protein in result_genename]
            else:
                results = [protein.geneID for protein in result_geneID]
        else:
            results = [protein.protein_name for protein in result_protein_name]
    else:
        results = [protein.uniprot_ID for protein in result_uniprot_ID]
    # results = [protein.geneID + "(" + protein.genename + ") " + protein.uniprot_ID + " (" + protein.protein_name +")" for protein in proteins]
    return JsonResponse({'suggestions': results})

def variant_autocomplete_view(request):
    query = request.GET.get('query', '')
    variants = Variant.objects.filter(Q(VariantMarker__icontains=query))
    if len(variants) > 0:
        results = [variant.VariantMarker + " in gene "+ variant.Gene_ID.genename +" (" + variant.Gene_ID.gene_id +")" for variant in variants]
    return JsonResponse({'suggestions': results})

def drug_autocomplete_view(request):
    query = request.GET.get('query', '')
    drugs = Drug.objects.filter(Q(drug_bankID__icontains=query))
    if len(drugs) > 0:
        results = [drug.drug_bankID + " - "+ drug.name for drug in drugs]
    return JsonResponse({'suggestions': results})

class Home(TemplateView):
    template_name = 'index_pharmcodb.html'
    context = {}

def common_menu(request):
    context = {
        'DOCUMENTATION_URL': settings.DOCUMENTATION_URL,  # Add DOCUMENTATION_URL to the context
    }
    return render(request, 'home/common_menu.html', context)


def variant_statistics(request):
    context = {
    }
    return render(request, 'home/variant_statistics.html', context)

def drug_target_network(request):
    context = {}
    return render(request, 'home/drug_and_target_network.html', context)
    # return render(request, 'home/drug_and_target_network copy.html', context)

def variant_lookup(request):
    context = {}
    objects = Variant.objects.all()[:20]
    variants = []
    for item in objects:
        variants.append({
            "VariantMarker": item.VariantMarker,
            'genename': item.Gene_ID.genename,
            'geneID': item.Gene_ID.gene_id,
        })
    if request.GET.get('variant'):
        variant = request.GET.get('variant')
        data = Variant.objects.filter(VariantMarker__icontains=variant)
        variants = []
        for item in data:
            variants.append({
                "VariantMarker": item.VariantMarker,
                'genename': item.Gene_ID.genename,
                'geneID': item.Gene_ID.gene_id,
            })
        return JsonResponse({'variants': variants})
    context["variants"] = variants
    return render(request, 'home/variant_lookup.html', context)

def drug_lookup(request):
    drug = request.GET.get('drug')
    clinical_status_dict = {0: "Nutraceutical", 1: "Experimental", 2: "Investigational", 3: "Approved", 4: "Vet approved", 5: "Illicit"}
    context = {}
    if drug:
        if drug != 'default':
            drug = drug.split(" - ")[0]
            data = Drug.objects.filter(
                Q(drug_bankID__icontains=drug) |
                Q(name__icontains=drug) 
            )
        else:
            data = Drug.objects.all()[:10]
        drugs = []
        for item in data:
            atc_code = DrugAtcAssociation.objects.filter(drug_id=item.drug_bankID).values_list('atc_id', flat=True).first()
            code = atc_code if atc_code is not None else "N/A"
            drugs.append({
                'drug_bankID': item.drug_bankID,
                'name': item.name,
                'atc_code': code,
                'pharmacogenomics_note': "coming soon",
                'Clinical_status': clinical_status_dict.get(item.Clinical_status)
            })

        return JsonResponse({'drugs': drugs})
    else:
        data = Drug.objects.all()[:10]
        drugs = []
        for item in data:
            atc_code = DrugAtcAssociation.objects.filter(drug_id=item.drug_bankID).values_list('atc_id', flat=True).first()
            code = atc_code if atc_code is not None else "N/A"

            drugs.append({
                'drug_bankID': item.drug_bankID,
                'name': item.name,
                'atc_code': code,
                'pharmacogenomics_note': "coming soon",
                'Clinical_status': clinical_status_dict.get(item.Clinical_status)
            })
        context["drugs"] = drugs
        return render(request, 'home/drug_lookup.html', context)
    
def get_atc_code(drug_bankID):
    try:
        drug_atc_association = DrugAtcAssociation.objects.filter(drug_id=drug_bankID).first()
        return drug_atc_association.atc_id.id if drug_atc_association else None
    except ObjectDoesNotExist:
        return None

def target_lookup(request):
    print("----------target lookup is called----------")
    target = request.GET.get('target')
    context = {}
    if target:
        if target != 'default':
            print("do we have target? :", target)
            proteins = Protein.objects.filter(
                Q(uniprot_ID__icontains=target) |
                Q(protein_name__icontains=target) |
                Q(geneID__icontains=target) |
                Q(genename__icontains=target)
            )
            print("target is not default, get proteins filtered by target, length = ", len(proteins))
        else:
            proteins = Protein.objects.all()[:10]
            print("target is default, get 10 records")
        items = []
        for item in proteins:
            interactions = Interaction.objects.filter(uniprot_ID=item.uniprot_ID)
            items.append({
                'uniprot_ID': item.uniprot_ID,
                'genename': item.genename,
                'geneID': item.geneID,
                'protein_name': item.protein_name,
                "drug_data": [
                    {
                        "drug_id": interaction.drug_bankID.drug_bankID,
                        "drug_name": interaction.drug_bankID.name.title(),
                        "atc_code": get_atc_code(interaction.drug_bankID)
                    }
                    for interaction in interactions
                ],
            })
        print("in the case of target is provided, length items = ", len(items))
        return JsonResponse({'items': items})
    else:
        # If no target parameter provided, get 10 records
        proteins = Protein.objects.all()[:10]
        items = []
        for item in proteins:
            interactions = Interaction.objects.filter(uniprot_ID=item.uniprot_ID)
            items.append({
                'uniprot_ID': item.uniprot_ID,
                'genename': item.genename,
                'geneID': item.geneID,
                'protein_name': item.protein_name,
                "drug_data": [
                    {
                        "drug_id": interaction.drug_bankID.drug_bankID,
                        "drug_name": interaction.drug_bankID.name,
                        "atc_code": get_atc_code(interaction.drug_bankID)
                    }
                    for interaction in interactions
                ],
            })
        context["items"] = items
        print("no target provided, get 10 records ")
        return render(request, 'home/target_lookup.html', context)
    
def target_statistics(request):
    context = {}
    return render(request, 'home/target_statistics.html', context)