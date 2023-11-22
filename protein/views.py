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


# from common.views import AbsBrowseSelection
# class BrowseSelection(AbsBrowseSelection):
#     title = 'SELECT A RECEPTOR (FAMILY)'
#     description = 'Select a target or family by searching or browsing in the right column.'
#     description = 'Select a receptor (family) by searching or browsing in the middle. The selection is viewed to' \
#                   + ' the right.'
#     docs = 'receptors.html'
#     target_input=False


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

class ProteinBrowser(TemplateView):

    template_name = 'protein_browser.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        browser_columns = ["uniprot_ID", "genename",
                           "geneID", "protein_name"]
        table = pd.DataFrame(columns=browser_columns)
        protein_data = Protein.objects.all().values_list(
            "uniprot_ID",
            "genename",
            "geneID",
            "protein_name"
        ).distinct()
        for data in protein_data:
            data_subset = {}
            data_subset['uniprot_ID'] = data[0]
            data_subset['genename'] = data[1]
            data_subset['geneID'] = data[2]
            data_subset['protein_name'] = data[3]

            table = table.append(data_subset, ignore_index=True)

        table.fillna('', inplace=True)
        # context = dict()
        print(table.head(3))
        context['Array'] = table.to_numpy()
        return context

#@cache_page(60 * 60 * 24 * 7)
def detail(request, slug):
    # get protein
    slug = slug.upper()

    try:
        if Protein.objects.filter(uniprot_ID=slug).exists():
            p = Protein.objects.get(uniprot_ID=slug)
            print("p --------- ",p)
        
    except:
        context = {'protein_no_found': slug}
        return render(request, 'protein_detail.html', context)

    # context_list=[]
    # for p in ps:

    # get family list
    uniprot_ID = p.uniprot_ID
    protein_name = p.protein_name


    context = {'uniprot_ID': uniprot_ID, 'protein_name': protein_name}


        # context_list.append(dic)


    return render(request, 'protein_detail.html', context)