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
from gene.models import Gene
from django.conf import settings
from django.http import JsonResponse

from django.db.models import Q

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

# def target_lookup2(request):
#     context = {}
#     proteins = Protein.objects.all()[:10]

#     if request.GET.get('target'):
#         target = request.GET.get('target')
#         print("do we have target ? : ", target)
#         data = Protein.objects.filter(Q(uniprot_ID__icontains=target) | Q(protein_name__icontains=target) | Q(geneID__icontains=target) | Q(genename__icontains=target))
#         proteins = []
#         for item in data:
#             proteins.append({
#                 'uniprot_ID': item.uniprot_ID,
#                 'genename': item.genename,
#                 'geneID': item.geneID,
#                 'protein_name': item.protein_name
#             })
#         return JsonResponse({'proteins': proteins})
#     context["proteins"] = proteins
#     return render(request, 'home/target_lookup2.html', context)

def target_lookup(request):
    target = request.GET.get('target')
    context = {}
    if target:
        if target != 'default':
            print("do we have target? :", target)
            data = Protein.objects.filter(
                Q(uniprot_ID__icontains=target) |
                Q(protein_name__icontains=target) |
                Q(geneID__icontains=target) |
                Q(genename__icontains=target)
            )
        else:
            data = Protein.objects.all()[:10]
        proteins = []
        for item in data:
            proteins.append({
                'uniprot_ID': item.uniprot_ID,
                'genename': item.genename,
                'geneID': item.geneID,
                'protein_name': item.protein_name
            })

        return JsonResponse({'proteins': proteins})
    else:
        # If no target parameter provided, get 10 records
        data = Protein.objects.all()[:10]
        proteins = []
        for item in data:
            proteins.append({
                'uniprot_ID': item.uniprot_ID,
                'genename': item.genename,
                'geneID': item.geneID,
                'protein_name': item.protein_name
            })
        context["proteins"] = proteins
        return render(request, 'home/target_lookup.html', context)
    
    

def target_statistics(request):
    context = {}
    return render(request, 'home/target_statistics.html', context)