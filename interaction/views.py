from django.shortcuts import render
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


from drug.models import Drug
from interaction.models import Interaction
from protein.models import Protein
from variant.models import Variant

# Create your views here.


class InteractionBrowser(TemplateView):

    template_name = 'interaction_browser.html'

    def get_context_data(self, **kwargs):

        context = super().get_context_data(**kwargs)

        browser_columns = ["gene_name",
                           "interaction_type",
                           "drugtype",
                           "uniprot_ID",
                           "geneID",
                           "#variants"
                           ]
        table = pd.DataFrame(columns=browser_columns)

        # interaction_data = Interaction.objects.filter(drug_bankID='DB00002').values_list(
        #     "uniprot_ID", "interaction_type")
        interaction_data = Interaction.objects.all().values_list(
            "uniprot_ID", "interaction_type")
        # drug_data = Drug.objects.filter(
        #     drug_bankID='DB00002').values_list("drugtype", "name")
        drug_data = Drug.objects.all().values_list("drugtype", "name")
        drugname=drug_data[0][1]

        if drug_data[0][0] == 1:
            drugtype = "Biotech"
        else:
            drugtype = "Small molecule"
      
        for data in interaction_data:
            data_subset = {}
            data_subset["uniprot_ID"] = data[0]
            data_subset["interaction_type"] = data[1].title()
            data_subset["drugtype"] = drugtype

            # Retrieve protein name
            genename = Protein.objects.filter(
                uniprot_ID=data[0]).values_list("genename")[0][0]
            data_subset["gene_name"] = genename

            # Retrieve gene ID
            geneID = Protein.objects.filter(
                uniprot_ID=data[0]).values_list("geneID")[0][0]
            data_subset["geneID"] = geneID

            # Retrieve number of variant
            markers = VariantMarker.objects.filter(
                geneID=geneID).values_list("markerID")
            data_subset["#variants"]=len(markers)

            table = table.append(data_subset, ignore_index=True)
            

        table.fillna('', inplace=True)
        # context = dict()
        print(table.head(3))
        print("--------------------  drug_data[0][0]: ", drug_data[0][0])
        length = len(table)
        context['Array'] = table.to_numpy()
        context['test'] = table.to_json(orient='records')
        context['drugname'] = drugname
        context['drugID'] = 'DB00002'
        context['length'] = length

        
        return context
