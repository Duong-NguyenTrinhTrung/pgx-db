from collections import Counter
import json
import numpy as np
from django.core import serializers
import pandas as pd
from django.core.cache import cache
from django.db.models import (
    Count,
    Q,
)
from django.http import (
    Http404,
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import (
    get_object_or_404,
    render,
)
from django.views.decorators.cache import cache_page
from django.views.decorators.csrf import csrf_exempt
from django.views.generic import TemplateView, ListView

from django_filters.views import FilterView
from drug.filters import AtcAnatomicalGroupFilter
from drug.models import (AtcAnatomicalGroup,
    AtcTherapeuticGroup,
    AtcPharmacologicalGroup,
    AtcChemicalGroup,
    AtcChemicalSubstance,
    DrugAtcAssociation,
    AdverseDrugReaction,
    SideEffect
)
from gene.models import Gene
from interaction.models import Interaction
from protein.models import Protein
from variant.models import GenebassVariant, GenebassPGx, GenebassVariantPGx, Variant, Pharmgkb
from disease.models import DrugDiseaseStudy, Disease

from .models import (
    Drug,
    DrugAtcAssociation, PreCachedDrugNetwork
)
from .services import DrugNetworkGetDataService, DrugsNetworkGetDataService
from time import perf_counter
import networkx as nx
from community import community_louvain
import matplotlib.pyplot as plt
import seaborn as sns
import os
from django.conf import settings
app_name = 'drug'
import logging
logger = logging.getLogger(__name__)

def serve_drug_data_json_file(request):
    atc_code = request.GET.get('atc_code')
    data = PreCachedDrugNetwork.objects.get(atc_code=atc_code)
    return JsonResponse(json.loads(data.drug_json_data), safe=False)

def serve_protein_data_json_file(request):
    atc_code = request.GET.get('atc_code')
    data = PreCachedDrugNetwork.objects.get(atc_code=atc_code)
    return JsonResponse(json.loads(data.protein_json_data), safe=False)
def serve_interaction_data_json_file(request):
    atc_code = request.GET.get('atc_code')
    data = PreCachedDrugNetwork.objects.get(atc_code=atc_code)
    return JsonResponse(json.loads(data.interaction_json_data), safe=False)
def serve_general_data_json_file(request):
    atc_code = request.GET.get('atc_code')
    data = PreCachedDrugNetwork.objects.get(atc_code=atc_code)
    print(type(json.loads(data.general_json_data)))
    print(type(json.loads(data.general_json_data)))
    # print(json.loads(data.general_json_data))
    return JsonResponse({'data': json.loads(data.general_json_data)})

class DiseaseAssociationByDrugView:
    def get_disease_association_by_drug(self, drug_id):
        if drug_id is not None:
            if cache.get("get_disease_association_by_drug_"+drug_id):
                response_data = cache.get("get_disease_association_by_drug_"+drug_id)
            else:
                result = []
                try:
                    drug = Drug.objects.get(drug_bankID=drug_id)
                    if drug:
                        associations = DrugDiseaseStudy.objects.filter(drug_bankID=drug_id)
                        if len(associations):
                            for association in associations:
                                    temp = {
                                            "Disease name": association.disease_name.disease_name,
                                            "Disease class": association.disease_name.disease_class,
                                            "Clinical trial phase": association.clinical_trial,
                                            "Reference link": association.link,
                                            }
                                    result.append(temp)
                        response_data = {
                            f"Disease(s) associated with the drug {drug.name} ({drug_id})": result,
                        }
                        cache.set("get_disease_association_by_drug_"+drug_id, response_data, timeout=60 * 15)
                    return response_data
                except:
                    raise Http404("Drug does not exist")


class AdrByDrugView:
    def get_drug_adr_for_api(self, drug_id):
        if drug_id is not None:
            if cache.get("get_drug_adr_"+drug_id):
                response_data = cache.get("get_drug_adr_"+drug_id)
            else:
                result = []
                adr = AdverseDrugReaction.objects.filter(drug_bankID=drug_id)
                if len(adr):
                    se_pair_list = adr.first().adr_data.split(", ")
                    for pair in se_pair_list:
                        if pair:
                            se_name = " ".join(pair.split()[:-1])
                            percentage = float(pair.split()[-1][1:-2])
                            se = SideEffect.objects.filter(side_effect_name=se_name)
                            if se:
                                definition = se.first().side_effect_definition
                            else:
                                definition = "NA"
                            temp = {
                                    "Side effect": se_name,
                                    "Definition": definition,
                                    "Frequency (in percentage)": percentage,
                                    }
                            result.append(temp)
                # Create a JSON response with the data
                response_data = {
                    "Adverse drug reaction": result,
                }
                
                cache.set("get_drug_adr_"+drug_id, response_data, timeout=60 * 15)
            return response_data

def drawNetworkAndSaveInAPlot(G, pat, name, title):
    # Create a simple graph
    # G = nx.Graph()
    # G.add_edges_from([(1, 2), (1, 3), (2, 3), (2, 4), (3, 4), (4, 5)])

    # Visualize the graph
    pos = nx.spring_layout(G, seed=42)  # Set seed for reproducibility
    nx.draw(G, pos, with_labels=True, font_weight='bold', node_color='skyblue', node_size=1000, font_size=10)

    # Assign colors to nodes based on community
    # colors = [partition[node] for node in G.nodes]

    # Draw the graph with nodes colored by community
    # nx.draw(G, pos, node_color=colors, cmap=plt.cm.get_cmap('viridis'), with_labels=True, font_weight='bold', node_size=1000, font_size=10)

    # plt.title("Simple Graph with Fake Data")
    plt.title(title)
    plt.show()
    plt.savefig(path+"/"+name+".png")

# from drug.models import (AtcAnatomicalGroup,
#     AtcChemicalGroup,
#     AtcChemicalSubstance,
#     AtcPharmacologicalGroup,
#     AtcTherapeuticGroup,
#     DrugAtcAssociation,
# )

def sort_dict(my_dict):
    # Sorting in descending order by values
    sorted_items_desc = sorted(my_dict.items(), key=lambda item: item[1], reverse=True)
    # Converting sorted items back to a dictionary for descending order
    sorted_dict_desc = dict(sorted_items_desc)
    return sorted_dict_desc


def get_adr_data(request):
    drugbank_id = request.GET.get('drugbank_id')
    adr_data = AdverseDrugReaction.objects.get(drug_bankID=drugbank_id).adr_data
    color1_data = {}
    color2_data = {}
    color3_data = {}
    color4_data = {}

    pairs = adr_data.split(", ")
    for pair in pairs:
        if pair!="":
            se = pair.split()[:-1]
            freq = float(pair.split()[-1][1:-2])
            if freq<=25:
                color1_data[" ".join(se)]=freq
            elif freq<=50:
                color2_data[" ".join(se)]=freq
            elif freq<=75:
                color3_data[" ".join(se)]=freq
            else:
                color4_data[" ".join(se)]=freq
    adr = {
            "color1": sort_dict(color1_data), 
            "color2": sort_dict(color2_data), 
            "color3": sort_dict(color3_data), 
            "color4": sort_dict(color4_data), 
        }
    return JsonResponse({'adr_data': adr})

def get_data_by_atc_for_network_ADR_comparison(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison") #compare
    if cache.get("get_data_by_atc_for_network_ADR_comparison_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_data_by_atc_for_network_ADR_comparison_"+atc_code+"_"+atc_comparison)
    else:
        atc_code_data = _get_adr_data_by_atc(atc_code)
        atc_comparison_data = _get_adr_data_by_atc(atc_comparison)
    response_data ={
        "atc_code": atc_code_data,
        "atc_comparison": atc_comparison_data,
        }
    return JsonResponse({"response_data": response_data})

def atc_comparison_autocomplete_view(request):
    query = request.GET.get('query', '').upper()
    results = []
    if len(query)==3:
        try:
            code = AtcTherapeuticGroup.objects.get(id=query)
            results.append(code.id+ " ("+code.name+")")
        except AtcTherapeuticGroup.DoesNotExist:
            pass
        codes = AtcPharmacologicalGroup.objects.filter(id__icontains=query)
        results+=[code.id+ " ("+code.name+")" for code in codes]
        codes = AtcChemicalGroup.objects.filter(id__icontains=query)
        results+=[code.id+ " ("+code.name+")" for code in codes]
        codes = AtcChemicalSubstance.objects.filter(id__icontains=query)
        results+=[code.id+ " ("+code.name+")" for code in codes]
    else:
        if len(query)==4:
            try:
                code = AtcPharmacologicalGroup.objects.get(id=query)
                results.append(code.id+ " ("+code.name+")")
            except AtcPharmacologicalGroup.DoesNotExist:
                pass
            codes = AtcChemicalGroup.objects.filter(id__icontains=query)
            results+=[code.id+ " ("+code.name+")" for code in codes]
            codes = AtcChemicalSubstance.objects.filter(id__icontains=query)
            results+=[code.id+ " ("+code.name+")" for code in codes]
        else:
            if len(query)==5:
                try:
                    code = AtcChemicalGroup.objects.get(id=query)
                    results.append(code.id+ " ("+code.name+")")
                except AtcChemicalGroup.DoesNotExist:
                    pass
                codes = AtcChemicalSubstance.objects.filter(id__icontains=query)
                results+=[code.id+ " ("+code.name+")" for code in codes]
            else:
                if len(query)==7:
                    try:
                        code = AtcChemicalSubstance.objects.get(id=query)
                        results.append(code.id+ " ("+code.name+")")
                    except AtcChemicalSubstance.DoesNotExist:
                        pass
                    
    results = list(set(results))
    # print("results before sorted ", results)
    # results = sorted(results, key=lambda x: x.split()[0])
    # results = sorted(results, key=lambda x: len(x.split()[0]))
    results = sorted(results, key=lambda x: (len(x.split()[0]), x.split()[0]))

    # print("results after sorted ", results)
    return JsonResponse({'suggestions': results})

def get_drug_network(request):

    drug_bank_id = request.GET.get('drug_bank_id')

    # Retrieve the drug object based on the drugbank_id
    try:
        drug = Drug.objects.get(drug_bankID=drug_bank_id)
    except Drug.DoesNotExist:
        raise Http404("Drug does not exist")

    context = {
        'drug_bank_id': drug_bank_id,
    }

    return render(request, 'drug_network.html', context)

def get_drugs_network(request):
    """
    Get the network data for a list of drugs
    """

    drug_bank_ids = request.GET.get('drug_bank_ids')
    drug_bank_ids = drug_bank_ids.split(',')
    # drug_bank_ids = ["DB00001", "DB00004", "DB00007", "DB00093", "DB00011"]
    context = {
        'drug_bank_ids': drug_bank_ids,
    }

    return render(request, 'drug_network.html', context)

# Retrieve data for one general set 
def get_drug_general_data(request, drug_bank_id):

    # Retrieve the drug object based on the drugbank_id
    try:
        drug = Drug.objects.get(drug_bankID=drug_bank_id)
    except Drug.DoesNotExist:
        raise Http404("Drug does not exist")
    # import pdb
    # pdb.set_trace()
    data = DrugNetworkGetDataService(drug=drug).get_general_data() # without s

    return JsonResponse(data, safe=False)

# Retrieve data for many general sets
def get_drugs_general_data(request):
    """
    Get the general data for a list of drugs
    """

    drug_bank_ids = request.GET.get('drug_bank_ids')
    drug_bank_ids = drug_bank_ids.split(',')
    if cache.get("drugs_general_data_" + "_".join(drug_bank_ids)) is not None:
        data = cache.get("drugs_general_data_" + "_".join(drug_bank_ids))
    else:
        data = DrugsNetworkGetDataService(drug_bank_ids=drug_bank_ids).get_general_data() # with s
        cache.set("drugs_general_data_" + "_".join(drug_bank_ids), data, 60 * 60)

    return JsonResponse({"data": data}, safe=False)

# Retrieve data for one drug
def get_drug_data(request, drug_bank_id):

    # Retrieve the drug object based on the drugbank_id
    try:
        drug = Drug.objects.get(drug_bankID=drug_bank_id)
    except Drug.DoesNotExist:
        raise Http404("Drug does not exist")

    data = DrugNetworkGetDataService(drug=drug).get_drug_data()

    
    return JsonResponse(data, safe=False)

# Retrieve data for one interaction
def get_drug_interaction_data(request, drug_bank_id):

    # Retrieve the drug object based on the drugbank_id
    try:
        drug = Drug.objects.get(drug_bankID=drug_bank_id)
    except Drug.DoesNotExist:
        raise Http404("Drug does not exist")

    data = DrugNetworkGetDataService(drug=drug).get_interaction_data()

    return JsonResponse(data, safe=False)

# Retrieve data for one protein
def get_drug_protein_data(request, drug_bank_id):

    # Retrieve the drug object based on the drugbank_id
    try:
        drug = Drug.objects.get(drug_bankID=drug_bank_id)
    except Drug.DoesNotExist:
        raise Http404("Drug does not exist")

    data = DrugNetworkGetDataService(drug=drug).get_protein_data()

    return JsonResponse(data, safe=False)






# Retrieve data for many drugs
def get_drugs_data(request):
    """
    Get the drug data for a list of drugs
    """

    drug_bank_ids = request.GET.get('drug_bank_ids')
    drug_bank_ids = drug_bank_ids.split(',')

    data = DrugsNetworkGetDataService(drug_bank_ids=drug_bank_ids).get_drug_data()
    # Serialize the queryset to JSON
    serialized_data = serializers.serialize('json', data)

    # Return the serialized data in a JsonResponse
    return JsonResponse(serialized_data, safe=False)


    # return JsonResponse(data, safe=False)

# Retrieve data for many interactions
def get_drugs_interaction_data(request):
    """
    Get the interaction data for a list of drugs
    """

    drug_bank_ids = request.GET.get('drug_bank_ids')
    drug_bank_ids = drug_bank_ids.split(',')

    data = DrugsNetworkGetDataService(drug_bank_ids=drug_bank_ids).get_interaction_data()

    return JsonResponse(data, safe=False)

# Retrieve data for many proteins
def get_drugs_protein_data(request):
    """
    Get the protein data for a list of drugs
    """

    drug_bank_ids = request.GET.get('drug_bank_ids')
    drug_bank_ids = drug_bank_ids.split(',')

    data = DrugsNetworkGetDataService(drug_bank_ids=drug_bank_ids).get_protein_data()

    return JsonResponse(data, safe=False)


# Then in this view function, we add drugbank_id as a parameter
def drug_atc_expansion(request, drugbank_id):  # put a parameter drugbank_id here

    context = {}

    # Specify the drug of interest
    drug_name = "Insulin human"

    # Retrieve the drug object based on the drugbank_id
    # And change the code getting drug to bellow
    # drug = get_object_or_404(Drug, drug_bankID=drugbank_id)
    drug = Drug.objects.get(drug_bankID=drugbank_id)

    # Get the related ATC code of the drug
    atc_code = DrugAtcAssociation.objects.filter(drug_id=drug).values_list('atc_id_id')
    context["num_substance"] = len(atc_code)
    num_list = [num + 1 for num in range(len(atc_code))]
    context['num_list'] = num_list
    atc_anatomical_group_list = list(
        set([x[0][0] + " (" + AtcAnatomicalGroup.objects.filter(id=x[0][0]).values_list('name', flat=True)[0] + ")" for
             x in atc_code]))
    atc_therapeutic_group_list = list(
        set([x[0][:3] + " (" + AtcTherapeuticGroup.objects.filter(id=x[0][0:3]).values_list('name', flat=True)[0] + ")"
             for x in atc_code]))
    atc_pharmacological_group_list = list(set([x[0][:4] + " (" +
                                               AtcPharmacologicalGroup.objects.filter(id=x[0][0:4]).values_list('name',
                                                                                                                flat=True)[
                                                   0] + ")" for x in atc_code]))
    atc_chemical_group_list = list(
        set([x[0][:5] + " (" + AtcChemicalGroup.objects.filter(id=x[0][0:5]).values_list('name', flat=True)[0] + ")" for
             x in atc_code]))
    atc_chemical_substance_list = list(
        set([x[0] + " (" + AtcChemicalSubstance.objects.filter(id=x[0][0:7]).values_list('name', flat=True)[0] + ")" for
             x in atc_code]))

    drugListDict = {}
    # codeNameListDict = {}
    for code in atc_anatomical_group_list:
        temp = DrugAtcAssociation.objects.filter(atc_id__id__startswith=code).values_list('drug_id__drug_bankID',
                                                                                          flat=True)
        drugListDict[code] = list(set([item for item in temp]))
        # name=AtcAnatomicalGroup.objects.filter(id=code).values_list('name', flat=True)[0]
        # codeNameListDict[code]=name
    for code in atc_therapeutic_group_list:
        temp = DrugAtcAssociation.objects.filter(atc_id__id__startswith=code).values_list('drug_id__drug_bankID',
                                                                                          flat=True)
        drugListDict[code] = list(set([item for item in temp]))
        # name=AtcTherapeuticGroup.objects.filter(id=code).values_list('name', flat=True)[0]
        # codeNameListDict[code]=name
    for code in atc_pharmacological_group_list:
        temp = DrugAtcAssociation.objects.filter(atc_id__id__startswith=code).values_list('drug_id__drug_bankID',
                                                                                          flat=True)
        drugListDict[code] = list(set([item for item in temp]))
        # name=AtcPharmacologicalGroup.objects.filter(id=code).values_list('name', flat=True)[0]
        # codeNameListDict[code]=name
    for code in atc_chemical_group_list:
        temp = DrugAtcAssociation.objects.filter(atc_id__id__startswith=code).values_list('drug_id__drug_bankID',
                                                                                          flat=True)
        drugListDict[code] = list(set([item for item in temp]))
        # name=AtcChemicalGroup.objects.filter(id=code).values_list('name', flat=True)[0]
        # codeNameListDict[code]=name
    for code in atc_chemical_substance_list:
        temp = DrugAtcAssociation.objects.filter(atc_id__id__startswith=code).values_list('drug_id__drug_bankID',
                                                                                          flat=True)
        drugListDict[code] = list(set([item for item in temp]))
        # name=AtcChemicalSubstance.objects.filter(id=code).values_list('name', flat=True)[0]
        # codeNameListDict[code]=name


    # Convert the list to a JSON string
    json_drugList_data = json.dumps(drugListDict)
    # json_codeName_data = json.dumps(codeNameListDict)

    # Pass the JSON string to the template context
    context['json_drugList_data'] = json_drugList_data
    context['drugListDict'] = drugListDict
    # context['codeNameListDict'] = codeNameListDict
    # context['json_codeName_data'] = json_codeName_data
    context['atc_anatomical_group_list'] = atc_anatomical_group_list
    context['atc_therapeutic_group_list'] = atc_therapeutic_group_list
    context['atc_pharmacological_group_list'] = atc_pharmacological_group_list
    context['atc_chemical_group_list'] = atc_chemical_group_list
    context['atc_chemical_substance_list'] = atc_chemical_substance_list

    # return render(request, 'drug_atc_tabs.html', context)
    return render(request, 'drug_atc_tabs_horizontal.html', context)
    # return render(request, 'drug_atc_tabs-leftshape.html', context)


def search_drugs(request):
    # extracts the search query parameter named 'q' from the GET request's query parameters. If 'q' is not present, the variable query is assigned the value None
    query = request.GET.get('q')

    # This line filters the Drug model's objects based on the search query. It uses the icontains lookup to perform a case-insensitive search on both the name and aliases fields, using the '|' (OR) operator to combine the two queries.
    drugs = Drug.objects.filter(Q(name__icontains=query) | Q(aliases__icontains=query))

    # creates a list of distinct drug names from the queryset drugs. The values_list method retrieves a list of tuples containing the 'name' field values, and the flat=True argument turns it into a flat list. The distinct() method ensures that only unique drug names are included.
    drug_names = drugs.values_list('name', flat=True).distinct()

    # Get related ATC codes and associated drugs for each drug
    drug_info = []
    for drug in drugs:
        # filters the DrugAtcAssociation model's objects based on the drug's ATC associations. It selects objects whose 'atc_id' is included in the drug's related ATC associations.
        drug_atc_associations = DrugAtcAssociation.objects.filter(atc_id__in=drug.drugatcassociation.all())
        atc_codes = drug_atc_associations.values_list('atc_id__id', flat=True).distinct()

        atc_drug_map = {}
        for atc_code in atc_codes:
            associated_drugs = Drug.objects.filter(drugatcassociation__atc_id__id=atc_code)
            atc_drug_map[atc_code] = associated_drugs

        drug_info.append({
            'name': drug.name,
            'related_atc_codes': atc_codes,
            'atc_drug_map': atc_drug_map,
        })

    # Pass the list of drug names and related drug information to the template for rendering
    context = {
        'drug_names': drug_names,
        'query': query,
        'drug_info': drug_info,
    }
    return render(request, 'drug_search_results.html', context)


@cache_page(60 * 60 * 24 * 28)
def drugbrowser(request):
    # Get drugdata from here somehow

    name_of_cache = 'drug_browser'

    context = cache.get(name_of_cache)

    if context == None:
        context = list()

        drugs = Drug.objects.all()

        for drug in drugs:
            drug_bankID = drug.drug_bankID

            # retrieve drugtype
            drug = Drug.objects.select_related('drugtype').filter(drug_bankID=drug_bankID).first()
            if drug:
                drugtype = drug.drugtype.type_detail
            else:
                drugtype = None

            # retrieve drugname
            drugname = drug.name

            # retrieve groups
            drug = Drug.objects.select_related('groups').filter(drug_bankID=drug_bankID).first()
            if drug:
                groups = drug.groups.group_detail
            else:
                groups = None

            # retrieve categories
            drug = Drug.objects.select_related('categories').filter(drug_bankID=drug_bankID).first()
            if drug:
                categories = drug.categories.category_detail
            else:
                categories = None

            # retrieve description
            description = drug.description

            # retrieve superclass
            drug = Drug.objects.select_related('superclass').filter(drug_bankID=drug_bankID).first()
            if drug:
                superclass = drug.superclass.superclass_detail
            else:
                superclass = None

            # retrieve classname
            drug = Drug.objects.select_related('classname').filter(drug_bankID=drug_bankID).first()
            if drug:
                classname = drug.classname.class_detail
            else:
                classname = None

            # retrieve subclass
            drug = Drug.objects.select_related('subclass').filter(drug_bankID=drug_bankID).first()
            if drug:
                subclass = drug.subclass.subclass_detail
            else:
                subclass = None

            # retrieve direct_parent
            drug = Drug.objects.select_related('direct_parent').filter(drug_bankID=drug_bankID).first()
            if drug:
                direct_parent = drug.direct_parent.parent_detail
            else:
                direct_parent = None

            description = drug.description
            aliases = drug.aliases
            indication = drug.indication
            pharmacodynamics = drug.pharmacodynamics
            moa = drug.moa
            absorption = drug.absorption
            toxicity = drug.toxicity
            halflife = drug.halflife
            distribution_volume = drug.distribution_volume
            protein_binding = drug.protein_binding
            dosages = drug.dosages
            properties = drug.properties
            chEMBL = drug.chEMBL

            # retrieve pubChemCompound
            drug = Drug.objects.select_related('pubChemCompound').filter(drug_bankID=drug_bankID).first()
            if drug:
                pubChemCompound = drug.pubChemCompound.compound_detail
            else:
                pubChemCompound = None

            pubChemSubstance = drug.pubChemSubstance

            jsondata = {'drug_bankID': drug_bankID, 'drugtype': drugtype, 'drugname': drugname, 'groups': groups,
                        'categories': categories, 'description': description, 'aliases': aliases,
                        'superclass': superclass,
                        'classname': classname, 'subclass': subclass, 'direct_parent': direct_parent,
                        'indication': indication,
                        'pharmacodynamics': pharmacodynamics, 'moa': moa, 'absorption': absorption,
                        'toxicity': toxicity,
                        'halflife': halflife, 'distribution_volume': distribution_volume,
                        'protein_binding': protein_binding, 'dosages': dosages,
                        'properties': properties, 'chEMBL': chEMBL,
                        'pubChemCompound': pubChemCompound, 'pubChemSubstance': pubChemSubstance}
            context.append(jsondata)

        cache.set(name_of_cache, context, 60 * 60 * 24 * 28)

    return render(request, 'drug_browser.html', {'drugdata': context})


# This is a helper function that takes a request object and checks if it's an AJAX request. It does this by checking if the 'HTTP_X_REQUESTED_WITH' key in the request.META dictionary is set to 'XMLHttpRequest'. If it is, it returns True, otherwise it returns False.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def selection_autocomplete(request):
    if is_ajax(request=request):
        q = request.GET.get('term').strip()
        type_of_selection = request.GET.get('type_of_selection')
        results = []

        if type_of_selection != 'navbar': # we don't need this
            ps = Protein.objects.filter(Q(name__icontains=q) | Q(entry_name__icontains=q),
                                        species__in=(species_list),
                                        source__in=(protein_source_list)).exclude(
                family__slug__startswith=exclusion_slug).exclude(sequence_type__slug='consensus')[:10]
        else:
            ps = []
            redirect = '/drug/'
            ps1 = Drug.objects.filter(Q(drug_bankID__icontains=q) | Q(name__icontains=q) | Q(aliases__icontains=q))
            ps2 = Gene.objects.filter(Q(gene_id__icontains=q) | Q(genename__icontains=q))
            ps3 = Protein.objects.filter(Q(uniprot_ID__icontains=q) | Q(protein_name__icontains=q))
            ps4 = Disease.objects.filter(Q(disease_name__icontains=q) | Q(disease_UML_CUI__icontains=q))
            ps5 = Variant.objects.filter(Q(VariantMarker__icontains=q))

        for p in ps1:
            p_json = {}
            p_json['id'] = p.drug_bankID
            p_json['label'] = p.name
            p_json['type'] = 'drug'
            p_json['redirect'] = '/drug_lookup/?drugbank_id='
            p_json['category'] = 'Drugs'
            results.append(p_json)

        for p in ps2:
            p_json = {}
            p_json['id'] = p.gene_id
            p_json['label'] = p.genename
            p_json['type'] = 'Gene'
            p_json['redirect'] = '/gene/'
            p_json['category'] = 'Genes'
            results.append(p_json)

        for p in ps3:
            p_json = {}
            p_json['id'] = p.uniprot_ID
            p_json['label'] = p.protein_name
            p_json['type'] = 'Protein'
            p_json['redirect'] = '/target_lookup/?uniprot_id='
            p_json['category'] = 'Proteins'
            results.append(p_json)

        for p in ps4:
            p_json = {}
            p_json['id'] = p.disease_name
            p_json['label'] = p.disease_name
            p_json['type'] = 'Disease'
            p_json['redirect'] = '/disease_lookup/?disease_info='
            p_json['category'] = 'Diseases'
            results.append(p_json)

        for p in ps5:
            p_json = {}
            p_json['id'] = p.VariantMarker
            p_json['label'] = p.VariantMarker
            p_json['type'] = 'Variant'
            p_json['redirect'] = '/variant_lookup/?variant_marker='
            p_json['category'] = 'Variant'
            results.append(p_json)

        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    return HttpResponse(data, mimetype)


# Create your views here.
def get_drug_statistics(request):
    #0 -> Nutraceutical, 1 - Experimental, 2- Investigational, 3- Approved , 4 - Vet approved, 5 - Illicit

    no_of_others = len(list(set(Drug.objects.filter(Clinical_status__in=[0, 4, 5]).values_list("drug_bankID", flat=True))))
    no_of_experimental = len(list(set(Drug.objects.filter(Clinical_status=1).values_list("drug_bankID", flat=True))))
    no_of_investigational = len(list(set(Drug.objects.filter(Clinical_status=2).values_list("drug_bankID", flat=True))))
    no_of_approved = len(list(set(Drug.objects.filter(Clinical_status=3).values_list("drug_bankID", flat=True))))

    super_classes = ["Organoheterocyclic compounds", "Benzenoids", "Organic acids and derivatives", "None", "Lipids and lipid-like molecules", "Organic oxygen compounds", "Phenylpropanoids and polyketides", "Nucleosides, nucleotides, and analogues", "Organic nitrogen compounds", "Alkaloids and derivatives", "Mixed metal/non-metal compounds", "Organosulfur compounds", "Organic Polymers", "Homogeneous non-metal compounds", "Homogeneous metal compounds", "Organohalogen compounds", "Lignans, neolignans and related compounds", "Organophosphorus compounds", "Organometallic compounds", "Organic salts", "Hydrocarbon derivatives"]
    super_classes_displayed = ["Organoheterocyclic compounds", "Benzenoids", "Organic acids and derivatives", "Unknown superclass", "Lipids and lipid-like molecules", "Organic oxygen compounds", "Phenylpropanoids and polyketides", "Nucleosides, nucleotides, and analogues", "Organic nitrogen compounds", "Alkaloids and derivatives", "Mixed metal/non-metal compounds", "Organosulfur compounds", "Organic Polymers", "Homogeneous non-metal compounds", "Homogeneous metal compounds", "Organohalogen compounds", "Lignans, neolignans and related compounds", "Organophosphorus compounds", "Organometallic compounds", "Organic salts", "Hydrocarbon derivatives"]

    # context = {
    context = {
        "no_of_investigational": no_of_investigational, 
        "no_of_approved": no_of_approved, 
        "no_of_experimental": no_of_experimental, 
        "no_of_others": no_of_others, 
        "total": no_of_others + no_of_experimental + no_of_investigational + no_of_approved,
        "super_classes": super_classes_displayed,
        "biologic":
        {
            "experimental": [Drug.objects.filter(Q(drugtype__type_detail="Biotech") & Q(Clinical_status=1) & Q(superclass__superclass_detail=sc)).count() for sc in super_classes],
            "approve": [Drug.objects.filter(Q(drugtype__type_detail="Biotech") & Q(Clinical_status=3) & Q(superclass__superclass_detail=sc)).count() for sc in super_classes],
            "investigational": [Drug.objects.filter(Q(drugtype__type_detail="Biotech") & Q(Clinical_status=2) & Q(superclass__superclass_detail=sc)).count() for sc in super_classes],
            "other": [Drug.objects.filter(Q(drugtype__type_detail="Biotech") & ~Q(Clinical_status__in=[0, 4, 5]) & Q(superclass__superclass_detail=sc)).count() for sc in super_classes],
        },
        "small_molecule":
        {
            "experimental": [Drug.objects.filter(Q(drugtype__type_detail="Small Molecule") & Q(Clinical_status=1) & Q(superclass__superclass_detail=sc)).count() for sc in super_classes],
            "approve": [Drug.objects.filter(Q(drugtype__type_detail="Small Molecule") & Q(Clinical_status=3) & Q(superclass__superclass_detail=sc)).count() for sc in super_classes],
            "investigational": [Drug.objects.filter(Q(drugtype__type_detail="Small Molecule") & Q(Clinical_status=2) & Q(superclass__superclass_detail=sc)).count() for sc in super_classes],
            "other": [Drug.objects.filter(Q(drugtype__type_detail="Small Molecule") & ~Q(Clinical_status__in=[0, 4, 5]) & Q(superclass__superclass_detail=sc)).count() for sc in super_classes],
        },
    }
    return render(request, 'drugstatistics.html', context)



# Help from chatGPT.
def drug_interaction_detail(request, drugbank_id):
    # Retrieve the drug object
    drug = get_object_or_404(Drug, drug_bankID=drugbank_id)

    # a) Retrieve all the uniprot_ID of proteins that have interactions with the drug
    interactions = Interaction.objects.filter(drug_bankID=drug)
    protein_ids = [interaction.uniprot_ID.uniprot_ID for interaction in interactions]

    # b) Count for each interaction_type
    interaction_counts = interactions.values('interaction_type').annotate(count=Count('interaction_type'))

    # c) Retrieve the names of all AtcChemicalSubstance that associate with the drugs
    associations = DrugAtcAssociation.objects.filter(drug_id=drug)
    chemical_substance_names = [association.atc_id.id + "-" + association.atc_id.name for association in associations]

    # d) For each AtcChemicalSubstance, retrieve their parents until the top one
    atc_parents = []
    for association in associations:
        temp = []
        parent = association.atc_id.parent
        temp.append(parent.id + "-" + parent.name)
        while parent:
            if not (isinstance(parent, AtcAnatomicalGroup)):
                parent = parent.parent
                temp.append(parent.id + "-" + parent.name)
            else:
                break
        atc_parents.append(temp)

    context = {
        'drug': drug,
        'protein_ids': protein_ids,
        'interaction_counts': interaction_counts,
        # 'associations': associations,
        'chemical_substance_names': chemical_substance_names,
        'atc_parents': atc_parents
    }

    # return render(request, '_drug_detail.html', context)
    return render(request, 'drug_atc_tabs.html', context)


class AtcAnatomicalGroupListView(FilterView, ListView):
    template_name = 'atc_anatomical_group_list.html'
    filterset_class = AtcAnatomicalGroupFilter

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

    def get_queryset(self):
        return AtcAnatomicalGroup.objects.all()


def atc_lookup(request):
    atc_groups = AtcAnatomicalGroup.objects.all()
    # Uppercase the names before returning
    for group in atc_groups:
        group.name = group.name.upper()
    context = {
        'atc_groups': atc_groups,
    }
    return render(request, 'atc_code_lookup.html', context)


def format_atc_name(s):
    s = s.replace('"', '')
    return s

# Set timeout to a very high value (e.g., 10 years)
LONG_TIMEOUT = 60 * 60 * 24 * 30

@cache_page(LONG_TIMEOUT)
def atc_detail_view(request):
    start_time = perf_counter()
    group_id = request.GET.get('group_id')  # Retrieve group_id from the query parameter
    anatomic_group = None
    try:
        anatomic_group = AtcAnatomicalGroup.objects.get(id=group_id)
    except AtcAnatomicalGroup.DoesNotExist:
        pass

    group_name = anatomic_group.name if anatomic_group else ''

    group2s = AtcTherapeuticGroup.objects.filter(id__icontains=group_id)
    for group in group2s:
        group.name = format_atc_name(group.name)
    # group3s = AtcPharmacologicalGroup.objects.filter(id__icontains=group_id)
    # for group in group3s:
    #     group.name = format_atc_name(group.name)
    # group4s = AtcChemicalGroup.objects.filter(id__icontains=group_id)
    # for group in group4s:
    #     group.name = format_atc_name(group.name)
    # group5s = AtcChemicalSubstance.objects.filter(id__icontains=group_id)
    # for group in group5s:
    #     group.name = format_atc_name(group.name)
    context = {'group2s': group2s, "group_id": group_id,
               "group_name": group_name}
    end_time = perf_counter()
    response = render(request, 'atc_detail_view.html', context)
    response['atc_detail_view-Duration'] = end_time - start_time
    return response


@csrf_exempt  # Use this decorator for simplicity, but consider using a proper csrf token in production.
def atc_search_view(request):
    results = []
    if request.method == 'GET':
        inp = request.GET.get('atc_code_inp', '').strip()
        query_option = request.GET.get('query_option', '')
        if inp != "":       
            # Search "id" field in all models
            # if len(inp) > 7:
            #     print("invalid inp")
            # else:
            #     if len(inp) > 5:  # search for id length =7
            #         results += list(AtcChemicalSubstance.objects.filter(id__iexact=inp).values('id', 'name'))
            #     else:
            #         if len(inp) == 5:  # search for id length =5
            #             results += list(AtcChemicalGroup.objects.filter(id__iexact=inp).values('id', 'name'))
            #         else:
            #             if len(inp) == 4:  # search for id length =5
            #                 results += list(
            #                     AtcPharmacologicalGroup.objects.filter(id__iexact=inp).values('id', 'name'))
            #             else:
            #                 if len(inp) == 3:  # search for id length =5
            #                     results += list(
            #                         AtcTherapeuticGroup.objects.filter(id__iexact=inp).values('id', 'name'))
            #                 else:
            #                     results += list(
            #                         AtcAnatomicalGroup.objects.filter(id__iexact=inp).values('id', 'name'))
            if query_option == 'containing':
                # Search "name" field in all models
                results += list(AtcAnatomicalGroup.objects.filter(Q(id__icontains=inp)|Q(name__icontains=inp)).values('id', 'name'))
                print("results  AtcAnatomicalGroup contains: ", len(results), results)
                results += list(AtcTherapeuticGroup.objects.filter(Q(id__icontains=inp)|Q(name__icontains=inp)).values('id', 'name'))
                print("results  AtcTherapeuticGroup contains: ", len(results), results)
                results += list(
                    AtcPharmacologicalGroup.objects.filter(Q(id__icontains=inp)|Q(name__icontains=inp)).values('id', 'name'))
                print("results  AtcPharmacologicalGroup contains: ", len(results), results)
                results += list(AtcChemicalGroup.objects.filter(Q(id__icontains=inp)|Q(name__icontains=inp)).values('id', 'name'))
                print("results  AtcChemicalGroup contains: ", len(results), results)
                results += list(AtcChemicalSubstance.objects.filter(Q(id__icontains=inp)|Q(name__icontains=inp)).values('id', 'name'))
                print("results AtcChemicalSubstancecontains: ", len(results), results)
            elif query_option == 'startingwith':
                # Search "id" field in all models
                results += list(AtcAnatomicalGroup.objects.filter(Q(id__istartswith=inp)|Q(name__istartswith=inp)).values('id', 'name'))
                results += list(AtcTherapeuticGroup.objects.filter(Q(id__istartswith=inp)|Q(name__istartswith=inp)).values('id', 'name'))
                results += list(
                    AtcPharmacologicalGroup.objects.filter(Q(id__istartswith=inp)|Q(name__istartswith=inp)).values('id', 'name'))
                results += list(AtcChemicalGroup.objects.filter(Q(id__istartswith=inp)|Q(name__istartswith=inp)).values('id', 'name'))
                results += list(AtcChemicalSubstance.objects.filter(Q(id__istartswith=inp)|Q(name__istartswith=inp)).values('id', 'name'))

        for rs in results:
            rs["name"] = format_atc_name(rs["name"])
        context = {"query_option": query_option, "search_result": results, "input": inp}
        return render(request, 'atc_search_result.html', context)
    return render(request, 'atc_search_result.html', {"results": results})


def get_drug_atc_association(request):
    atc_code = request.GET.get("atc_code")
    if cache.get("get_drug_atc_association_"+atc_code):
        response_data = cache.get("get_drug_atc_association_"+atc_code)
    else:
        allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
        drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
        undup_drugs = list(set(drugs))
        associations = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
        total_interaction = 0
        interacted_protein = []
        associations_list = [
            {"drug_bankID": assoc.drug_bankID, "name": assoc.name, "description": assoc.description, "target_list": [ {"genename": item.uniprot_ID.genename, "gene_id": item.uniprot_ID.geneID, "uniProt_ID": item.uniprot_ID.uniprot_ID, "moa": item.interaction_type,  "count_drug": len(Interaction.objects.filter(uniprot_ID=item.uniprot_ID))} for item in Interaction.objects.filter(drug_bankID=assoc)]}
            for assoc in associations]
        for association in associations_list:
            total_interaction+=len(association.get("target_list"))
            for target in association.get("target_list"):
                interacted_protein.append(target.get("uniProt_ID"))
        interacted_protein = list(set(interacted_protein))

        # Create a JSON response with the data
        response_data = {
            "associations": associations_list,
            "atc_code": atc_code,
            "total_interaction": total_interaction,
            "no_of_interacted_protein":len(interacted_protein),
        }
        # Check the length of atc_code and set the cache with an appropriate timeout
        if len(atc_code) <= 5:
            # Set cache expiration to one year (365 days * 24 hours * 60 minutes * 60 seconds)
            cache_timeout = 365 * 24 * 60 * 60
            cache.set("get_drug_atc_association_"+atc_code, response_data, timeout=cache_timeout)
        else:
            # Set cache expiration to the default value (e.g., 15 minutes)
            cache.set("get_drug_atc_association_"+atc_code, response_data, timeout=60 * 15)
    return JsonResponse(response_data)


#helper function
def _get_clinical_pgx_data_by_drug(drug_id):
    cache_str = "get_clinical_pgx_data_by_drug_"+drug_id
    if cache.get(cache_str):
        response_data = cache.get(cache_str)
    else:
        interactions = Interaction.objects.filter(drug_bankID=drug_id)
        response_data = []
        # drug = Drug.objects.get()
        for interaction in interactions:
            gene_id = interaction.uniprot_ID.geneID
            gene_name = interaction.uniprot_ID.genename
            pharmgkb_data = Pharmgkb.objects.filter(Q(geneid=gene_id)&Q(drugbank_id=drug_id))
            if len(pharmgkb_data) != 0:
                    response_data.append({
                            "gene_name": gene_name,
                            "drug_id": drug_id,
                            "moa": interaction.interaction_type.title(),
                            "clinical_data": [
                                {
                                    "Variant_or_Haplotypes": item.Variant_or_Haplotypes,
                                    "PMID": item.PMID,
                                    "Phenotype_Category": str(item.Phenotype_Category),
                                    "Significance": str(item.Significance),
                                    "Notes": str(item.Notes),
                                    "Sentence": str(item.Sentence),
                                    "Alleles": str(item.Alleles),
                                    "P_Value": str(item.P_Value),
                                    "Biogeographical_Groups": str(item.Biogeographical_Groups),
                                    "Study_Type": str(item.Study_Type),
                                    "Study_Cases": str(item.Study_Cases),
                                    "Study_Controls": str(item.Study_Controls),
                                    "Direction_of_effect": str(item.Direction_of_effect),
                                    "PD_PK_terms": str(item.PD_PK_terms),
                                    "Metabolizer_types": str(item.Metabolizer_types),
                                } 
                                for item in pharmgkb_data
                                # if all( 
                                #     value is not None and float(value) 
                                #     for value in [genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden]
                                # )
                                # if all(
                                #     value not in [float('inf'), float('-inf')] and value is not None
                                #     for value in [genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden]
                                # )
                            ]
                    })
        if len(response_data)>0:
            cache.set(cache_str, response_data, 60*60)
    return response_data

def get_adr_data_by_atc(request):
    atc_code = request.GET.get("atc_code")
    response_data = _get_adr_data_by_atc(atc_code)
    return JsonResponse(response_data, safe=False)

#helper function
def _get_adr_data_by_atc(atc_code):
    cache_str = "get_adr_data_by_atc_"+atc_code
    if cache.get(cache_str):
        response_data = cache.get(cache_str)
    else:
        drugs = DrugAtcAssociation.objects.filter(atc_id__id__startswith=atc_code).select_related('drug_id').values_list("drug_id", flat=True)
        undup_drugs = list(set(drugs))
        drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
        response_data=[]
        for drug_id in drug_objs:
            adr = AdverseDrugReaction.objects.filter(drug_bankID=drug_id)
            result=[]
            if len(adr):
                se_pair_list = adr.first().adr_data.split(", ")
                for pair in se_pair_list:
                    if pair:
                        se_name = " ".join(pair.split()[:-1])
                        percentage = float(pair.split()[-1][1:-2])
                        se = SideEffect.objects.filter(side_effect_name=se_name)
                        if se:
                            definition = se.first().side_effect_definition
                        else:
                            definition = "NA"
                        temp = {
                                "Side effect": se_name,
                                "Definition": definition,
                                "Frequency (in percentage)": percentage,
                                }
                        result.append(temp)
                result = sorted(result, key=lambda x: x["Frequency (in percentage)"], reverse=True)
                response_data.append({"drug_id": drug_id.drug_bankID, "drug_name": drug_id.name, "adr_data": result})    
        if len(response_data)>0:
            cache.set(cache_str, response_data, 60*60)
    return response_data

def get_clinical_pgx_data_by_drug(request):
    drug_id = request.GET.get("drug_id")
    response_data = _get_clinical_pgx_data_by_drug(drug_id)
    return JsonResponse(response_data, safe=False)

#helper function
def _get_clinical_pgx_data_by_atc(atc_code):
    cache_str = "get_clinical_pgx_data_by_atc_"+atc_code
    if cache.get(cache_str):
        response_data = cache.get(cache_str)
    else:
        allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
        drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
        undup_drugs = list(set(drugs))
        drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
        response_data=[]
        for drug in drug_objs:
            interactions = Interaction.objects.filter(drug_bankID=drug)
            for interaction in interactions:
                gene_id = interaction.uniprot_ID.geneID
                gene_name = interaction.uniprot_ID.genename
                pharmgkb_data = Pharmgkb.objects.filter(Q(geneid=gene_id)&Q(drugbank_id=drug))
                if len(pharmgkb_data) != 0:
                        response_data.append({
                                "gene_name": gene_name,
                                "drug_id": drug.drug_bankID,
                                "moa": interaction.interaction_type.title(),
                                "clinical_data": [
                                    {
                                        "Variant_or_Haplotypes": item.Variant_or_Haplotypes,
                                        "PMID": item.PMID,
                                        "Phenotype_Category": str(item.Phenotype_Category),
                                        "Significance": str(item.Significance),
                                        "Notes": str(item.Notes),
                                        "Sentence": str(item.Sentence),
                                        "Alleles": str(item.Alleles),
                                        "P_Value": str(item.P_Value),
                                        "Biogeographical_Groups": str(item.Biogeographical_Groups),
                                        "Study_Type": str(item.Study_Type),
                                        "Study_Cases": str(item.Study_Cases),
                                        "Study_Controls": str(item.Study_Controls),
                                        "Direction_of_effect": str(item.Direction_of_effect),
                                        "PD_PK_terms": str(item.PD_PK_terms),
                                        "Metabolizer_types": str(item.Metabolizer_types),
                                    } 
                                    for item in pharmgkb_data
                                    # if all( 
                                    #     value is not None and float(value) 
                                    #     for value in [genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden]
                                    # )
                                    # if all(
                                    #     value not in [float('inf'), float('-inf')] and value is not None
                                    #     for value in [genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden]
                                    # )
                                ]
                        })
        if len(response_data)>0:
            cache.set(cache_str, response_data, 60*60)
    return response_data

def get_clinical_pgx_data_by_atc(request):
    atc_code = request.GET.get("atc_code")
    response_data = _get_clinical_pgx_data_by_atc(atc_code)
    return JsonResponse(response_data, safe=False)


# a helper function
def get_genebased_data_from_genebass(atc_code):
    cache_str = "gene_based_burden_data_by_atc_"+atc_code
    if cache.get(cache_str):
        response_data = cache.get(cache_str)
    else:
        allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
        drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
        undup_drugs = list(set(drugs))
        drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
        response_data=[]
        interaction_data = []
        for drug in drug_objs:
            interactions = Interaction.objects.filter(drug_bankID=drug)
            for interaction in interactions:
                gene_id = interaction.uniprot_ID.geneID
                gene_name = interaction.uniprot_ID.genename
                data_genebass = GenebassPGx.objects.filter(Q(gene_id=gene_id)&Q(drugbank_id=drug.drug_bankID))
                if len(data_genebass) != 0:
                        response_data.append({
                                "gene_name": gene_name,
                                "drug_id": drug.drug_bankID,
                                "moa": interaction.interaction_type.title(),
                                "burden_data": [
                                    {
                                        "phenocode": genebass.phenocode.phenocode,
                                        "annotation": genebass.annotation,
                                        "n_cases": str(genebass.n_cases),
                                        "n_controls": str(genebass.n_controls),
                                        "Pvalue": str(genebass.Pvalue),
                                        "Pvalue_Burden": str(genebass.Pvalue_Burden),
                                        "Pvalue_SKAT": str(genebass.Pvalue_SKAT),
                                        "BETA_Burden": str(genebass.BETA_Burden),
                                        "SE_Burden": str(genebass.SE_Burden),
                                    } 
                                    for genebass in data_genebass
                                    # if all( 
                                    #     value is not None and float(value) 
                                    #     for value in [genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden]
                                    # )
                                    # if all(
                                    #     value not in [float('inf'), float('-inf')] and value is not None
                                    #     for value in [genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden]
                                    # )
                                ]
                        })
        if len(response_data)>0:
            cache.set(cache_str, response_data, 60*60)
    return response_data

# a helper function
def get_genebased_data_from_genebass_by_drug(drug_id):
    cache_str = "get_genebased_data_from_genebass_by_drug_"+drug_id
    if cache.get(cache_str):
        response_data = cache.get(cache_str)
    else:   
            response_data = []
            interactions = Interaction.objects.filter(drug_bankID=drug_id)
            for interaction in interactions:
                gene_id = interaction.uniprot_ID.geneID
                gene_name = interaction.uniprot_ID.genename
                data_genebass = GenebassPGx.objects.filter(Q(gene_id=gene_id)&Q(drugbank_id=drug_id))
                if len(data_genebass) != 0:
                        response_data.append({
                                "gene_name": gene_name,
                                "drug_id": drug_id,
                                "moa": interaction.interaction_type.title(),
                                "burden_data": [
                                    {
                                        "phenocode": genebass.phenocode.phenocode,
                                        "annotation": genebass.annotation,
                                        "n_cases": str(genebass.n_cases),
                                        "n_controls": str(genebass.n_controls),
                                        "Pvalue": str(genebass.Pvalue),
                                        "Pvalue_Burden": str(genebass.Pvalue_Burden),
                                        "Pvalue_SKAT": str(genebass.Pvalue_SKAT),
                                        "BETA_Burden": str(genebass.BETA_Burden),
                                        "SE_Burden": str(genebass.SE_Burden),
                                    } 
                                    for genebass in data_genebass
                                    # if all( 
                                    #     value is not None and float(value) 
                                    #     for value in [genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden]
                                    # )
                                    # if all(
                                    #     value not in [float('inf'), float('-inf')] and value is not None
                                    #     for value in [genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden]
                                    # )
                                ]
                        })
    if len(response_data)>0:
        cache.set(cache_str, response_data, 60*60)
    return response_data

def get_gene_based_burden_data_by_drug(request):
    drug_id = request.GET.get("drug_id")
    response_data = get_genebased_data_from_genebass_by_drug(drug_id)
    return JsonResponse(response_data, safe=False)

def get_gene_based_burden_data_by_atc(request):
    atc_code = request.GET.get("atc_code")
    response_data = get_genebased_data_from_genebass(atc_code)
    return JsonResponse(response_data, safe=False)

def get_variant_based_burden_data_by_drug(request):
    drug_id = request.GET.get("drug_id")
    if cache.get("get_variant_based_burden_data_by_drug_"+drug_id):
        response_data = cache.get("get_variant_based_burden_data_by_drug_"+drug_id)
    else:
        response_data=[]
        drug_id = request.GET.get("drug_id")
        gene_names = list(set(Interaction.objects.filter(drug_bankID=drug_id).values_list("uniprot_ID__genename", flat=True)))
        genebass_data = GenebassVariantPGx.objects.filter(
            drugbank_id=drug_id, genename__in=gene_names
        ).all().values(
            'genename', 
            'variant_marker__VariantMarker',
            'coding_description',
            'description',
            'annotation',
            'n_cases',
            'n_controls',
            'Pvalue',
            'BETA',
            'AC',
            'AF',
        )
        
        if len(genebass_data) != 0:
            response_data = [{"drug_id": drug_id,
                "interactions": list(Interaction.objects.filter(drug_bankID=drug_id).values("drug_bankID", "uniprot_ID__genename", "interaction_type")),
                "burden_data": list(genebass_data_portion),
                # "burden_data_full": list(genebass_data),
            }]
        if len(response_data)>0:
            cache.set("get_variant_based_burden_data_by_drug_"+drug_id, response_data, 60*60)
        else:
            print("no variant pgx data")
    return JsonResponse(response_data, safe=False)


def get_variant_based_burden_data_by_atc(request):
    atc_code = request.GET.get("atc_code")
    if cache.get("get_variant_based_data_by_atc_"+atc_code):
        response_data = cache.get("get_variant_based_data_by_atc_"+atc_code)
    else:
        allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
        drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
        undup_drugs = list(set(drugs))
        drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
        gene_names = list(set(Interaction.objects.filter(drug_bankID__in=undup_drugs).values_list("uniprot_ID__genename", flat=True)))
        response_data=[]
        for drug in drug_objs:
            genebass_data = GenebassVariantPGx.objects.filter(
                drugbank_id=drug, genename__in=gene_names
            ).all().values(
                'genename', 
                'variant_marker__VariantMarker',
                'coding_description',
                'description',
                'annotation',
                'n_cases',
                'n_controls',
                'Pvalue',
                'BETA',
                'AC',
                'AF',
            )
            
            if len(genebass_data) != 0:
                response_data.append(
                {
                    "drug_id": drug.drug_bankID,
                    "burden_data": list(genebass_data),
                    # "burden_data_full": list(genebass_data),
                })
            
        if len(response_data)>0:
            cache.set("get_variant_based_data_by_atc_"+atc_code, response_data, 60*60)
        else:
            print("no variant pgx data")
    return JsonResponse(response_data, safe=False)

def get_statistics_by_atc_for_ONE_atc_code_for_clinical_trial_phase_comparison(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
    phases = []
    for drug in drug_objs:
        associations = DrugDiseaseStudy.objects.filter(drug_bankID=drug)
        for association in associations:
            phases.append("Phase "+association.clinical_trial)
    return {"classes": list(Counter(phases).keys()), "class_count": list(Counter(phases).values())}

def get_statistics_by_atc_for_clinical_trial_phase_comparison(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_data_for_comparing_clinical_trial_phase_distribution_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_data_for_comparing_clinical_trial_phase_distribution_"+atc_code+"_"+atc_comparison)
    else:
        #max_value = max(my_dict, key=my_dict.get)
        data1 = get_statistics_by_atc_for_ONE_atc_code_for_clinical_trial_phase_comparison(atc_code)
        data2 = get_statistics_by_atc_for_ONE_atc_code_for_clinical_trial_phase_comparison(atc_comparison)
        if len(list(data1.get("class_count"))):
             max1 = max(list(data1.get("class_count")))
        else:
            max1 = 0
        if len(list(data2.get("class_count"))):
            max2 = max(list(data2.get("class_count")))
        else:
            max2 = 0
        response_data = {
            "atc_code": data1, 
            "atc_comparison": data2,
            "max_count": max(max1, max2) 
        }
        cache.set("get_data_for_comparing_clinical_trial_phase_distribution_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_statistics_by_atc_for_ONE_atc_code_for_MOA_comparison(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
    moas = []
    for drug in drug_objs:
        interactions = Interaction.objects.filter(drug_bankID=drug)
        for interaction in interactions:
            moas.append(interaction.interaction_type)
    return {"classes": list(Counter(moas).keys()), "class_count": list(Counter(moas).values())}

def get_statistics_by_atc_code_for_MOA_comparison(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_data_for_comparing_moa_distribution_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_data_for_comparing_moa_distribution_"+atc_code+"_"+atc_comparison)
    else:
        data1 = get_statistics_by_atc_for_ONE_atc_code_for_MOA_comparison(atc_code)
        data2 = get_statistics_by_atc_for_ONE_atc_code_for_MOA_comparison(atc_comparison)
        print("atc_code ",atc_code, " data1 ", data1)
        print("atc_comparison ",atc_comparison, " data2 ", data2)
        # max1 = max(list(data1.get("class_count")))
        # max2 = max(list(data2.get("class_count")))
        response_data = {
            "atc_code": data1, 
            "atc_comparison": data2,
            # "max_count": max(max1, max2) 
        }
        cache.set("get_data_for_comparing_moa_distribution_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_statistics_by_atc_for_detecting_community_drug_protein(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_statistics_by_ONE_atc_for_detecting_community_drug_protein_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_statistics_by_ONE_atc_for_detecting_community_drug_protein_"+atc_code+"_"+atc_comparison)
    else:
        response_data = {
            "atc_code":get_statistics_by_ONE_atc_for_detecting_community_drug_protein(atc_code), 
            "atc_comparison":get_statistics_by_ONE_atc_for_detecting_community_drug_protein(atc_comparison), 
        }
        cache.set("get_statistics_by_ONE_atc_for_detecting_community_drug_protein_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_statistics_by_ONE_atc_for_detecting_community_drug_protein(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    unique_drug_list = list(Drug.objects.filter(drug_bankID__in=undup_drugs).values_list("name", flat=True))
    unique_drug_list2 = ["*"+ d for d in unique_drug_list]
    G = nx.Graph()
    #adding nodes
    G.add_nodes_from(unique_drug_list2)
    interactions = list(Interaction.objects.filter(drug_bankID__name__in=unique_drug_list).values_list("uniprot_ID__genename", flat=True))
    interactions2 = ["@"+ g for g in list(set(interactions))]
    G.add_nodes_from(interactions2)

    #adding edges
    for drug in unique_drug_list:
        genenames = list(Interaction.objects.filter(drug_bankID__name=drug).values_list("uniprot_ID__genename", flat=True))
        for genename in genenames:
            G.add_edge("*"+drug, "@"+genename)

    #detect community
    partition = community_louvain.best_partition(G)
    partition_drug = [{node:community_id} for node, community_id in partition.items() if node[0]=="*"]
    partition_gene = [{node:community_id} for node, community_id in partition.items() if node[0]=="@"]
    return {"partition_drug":partition_drug, "partition_gene":partition_gene}

def get_statistics_by_atc_for_calculating_average_path_length_drug_protein(request):
    pass
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_protein_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_protein_"+atc_code+"_"+atc_comparison)
    else:
        response_data = {
            "atc_code":get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_protein(atc_code), 
            "atc_comparison":get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_protein(atc_comparison), 
        }
        cache.set("get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_disease_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_protein(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    unique_drug_list = list(Drug.objects.filter(drug_bankID__in=undup_drugs).values_list("name", flat=True))
    G = nx.Graph()
    #adding nodes
    G.add_nodes_from(unique_drug_list)
    interactions = list(Interaction.objects.filter(drug_bankID__name__in=unique_drug_list).values_list("uniprot_ID__genename", flat=True))
    G.add_nodes_from(interactions)

    #adding edges
    for drug in unique_drug_list:
        gene_names = list(Interaction.objects.filter(drug_bankID__name=unique_drug_list).values_list("uniprot_ID__genename", flat=True))
        for gene_name in gene_names:
            G.add_edge(drug, gene_name)

    response = {}
    is_connected = nx.is_connected(G)
    if not is_connected:
        connected_components = list(nx.connected_components(G))
        response["no_of_components"]=len(connected_components)
        temp=[]
        for component in connected_components:
            component_graph = G.subgraph(component)
            shortest_paths = nx.shortest_path_length(component_graph)

            average_shortest_path_length = nx.average_shortest_path_length(component_graph)
            # shortest_paths_dict = {}

            # for source_node, paths in shortest_paths:
            #     shortest_paths_dict[source_node] = dict(paths)
            temp.append({ "nodes":list(component_graph.nodes), "average_shortest_path_length":average_shortest_path_length})
        response["component_detail"] = temp
    else:
        shortest_paths = nx.shortest_path_length(G)
        average_shortest_path_length = nx.average_shortest_path_length(G)
        # shortest_paths_dict = {}
        # for source_node, paths in shortest_paths:
        #     shortest_paths_dict[source_node] = dict(paths)
        response = {"no_of_components":1, "component_detail":[{"nodes":list(G.nodes), "average_shortest_path_length":average_shortest_path_length}]}
    return response

def get_statistics_by_atc_for_calculating_average_path_length_drug_disease(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_disease_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_disease_"+atc_code+"_"+atc_comparison)
    else:
        response_data = {
            "atc_code":get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_disease(atc_code), 
            "atc_comparison":get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_disease(atc_comparison), 
        }
        cache.set("get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_disease_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_statistics_by_ONE_atc_for_calculating_average_path_length_drug_disease(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    unique_drug_list = list(Drug.objects.filter(drug_bankID__in=undup_drugs).values_list("name", flat=True))
    G = nx.Graph()
    #adding nodes
    G.add_nodes_from(unique_drug_list)
    associations = list(DrugDiseaseStudy.objects.filter(drug_bankID__name__in=unique_drug_list).values_list("disease_name__disease_name", flat=True))
    G.add_nodes_from(associations)

    #adding edges
    for drug in unique_drug_list:
        disease_names = list(DrugDiseaseStudy.objects.filter(drug_bankID__name=drug).values_list("disease_name__disease_name", flat=True))
        for disease_name in disease_names:
            G.add_edge(drug, disease_name)

    response = {}
    is_connected = nx.is_connected(G)
    if not is_connected:
        connected_components = list(nx.connected_components(G))
        response["no_of_components"]=len(connected_components)
        temp=[]
        for component in connected_components:
            component_graph = G.subgraph(component)
            shortest_paths = nx.shortest_path_length(component_graph)

            average_shortest_path_length = nx.average_shortest_path_length(component_graph)
            # shortest_paths_dict = {}

            # for source_node, paths in shortest_paths:
            #     shortest_paths_dict[source_node] = dict(paths)
            temp.append({ "nodes":list(component_graph.nodes), "average_shortest_path_length":average_shortest_path_length})
        response["component_detail"] = temp
    else:
        shortest_paths = nx.shortest_path_length(G)
        average_shortest_path_length = nx.average_shortest_path_length(G)
        # shortest_paths_dict = {}
        # for source_node, paths in shortest_paths:
        #     shortest_paths_dict[source_node] = dict(paths)
        response = {"no_of_components":1, "component_detail":[{"nodes":list(G.nodes), "average_shortest_path_length":average_shortest_path_length}]}
    return response
    

def get_statistics_by_atc_for_detecting_community_drug_disease(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_statistics_by_ONE_atc_for_detecting_community_drug_disease_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_statistics_by_ONE_atc_for_detecting_community_drug_disease_"+atc_code+"_"+atc_comparison)
    else:
        response_data = {
            "atc_code":get_statistics_by_ONE_atc_for_detecting_community_drug_disease(atc_code), 
            "atc_comparison":get_statistics_by_ONE_atc_for_detecting_community_drug_disease(atc_comparison), 
        }
        cache.set("get_statistics_by_ONE_atc_for_detecting_community_drug_disease_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_statistics_by_ONE_atc_for_detecting_community_drug_disease(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    unique_drug_list = list(Drug.objects.filter(drug_bankID__in=undup_drugs).values_list("name", flat=True))
    unique_drug_list2 = ["*"+ d for d in unique_drug_list]
    G = nx.Graph()
    #adding nodes
    G.add_nodes_from(unique_drug_list2)
    associations = list(DrugDiseaseStudy.objects.filter(drug_bankID__name__in=unique_drug_list).values_list("disease_name__disease_name", flat=True))
    associations2 = ["#"+ d for d in list(set(associations))]
    G.add_nodes_from(associations2)

    #adding edges
    for drug in unique_drug_list:
        disease_names = list(DrugDiseaseStudy.objects.filter(drug_bankID__name=drug).values_list("disease_name__disease_name", flat=True))
        for disease_name in disease_names:
            G.add_edge("*"+drug, "#"+disease_name)
    

    #detect community
    partition = community_louvain.best_partition(G)
    partition_drug = [{node:community_id} for node, community_id in partition.items() if node[0]=="*"]
    partition_disease = [{node:community_id} for node, community_id in partition.items() if node[0]=="#"]

    # # Assign colors to nodes based on community
    # colors = [partition[node] for node in G.nodes]

    # pos = nx.spring_layout(G, seed=42)  # Set seed for reproducibility
    # # Draw the graph with nodes colored by community
    # nx.draw(G, pos, node_color=colors, cmap=plt.cm.get_cmap('viridis'), with_labels=True,
    #         font_weight='bold', node_size=1000, font_size=10)

    # # Display the graph
    # plt.title("Communities Detected by Louvain Algorithm")
    # # plt.show()
    # plt.savefig("../static/community_"+atc_code+".png")
    return {"nodes": list(G.nodes), "edges": list(G.edges), "partition_drug":partition_drug, "partition_disease":partition_disease}

    
def get_statistics_by_atc_for_measure_centralization_drug_protein(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_statistics_by_atc_for_measure_centralization_drug_protein_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_statistics_by_atc_for_measure_centralization_drug_protein_"+atc_code+"_"+atc_comparison)
    else:
        response_data = {
            "atc_code":get_statistics_by_ONE_atc_for_measure_centralization_drug_protein(atc_code), 
            "atc_comparison":get_statistics_by_ONE_atc_for_measure_centralization_drug_protein(atc_comparison), 
        }
        cache.set("get_statistics_by_atc_for_measure_centralization_drug_protein_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_statistics_by_ONE_atc_for_measure_centralization_drug_protein(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    unique_drug_list = list(Drug.objects.filter(drug_bankID__in=undup_drugs).values_list("name", flat=True))
    unique_drug_list2 = ["*"+ d for d in unique_drug_list]
    G = nx.Graph()
    #adding nodes
    G.add_nodes_from(unique_drug_list2)
    interactions = list(Interaction.objects.filter(drug_bankID__name__in=unique_drug_list).values_list("uniprot_ID__genename", flat=True))
    interactions2 = ["@"+ g for g in list(set(interactions))]
    G.add_nodes_from(interactions2)

    #adding edges
    for drug in unique_drug_list:
        genenames = list(Interaction.objects.filter(drug_bankID__name=drug).values_list("uniprot_ID__genename", flat=True))
        for genename in genenames:
            G.add_edge("*"+drug, "@"+genename)
    
    #calculate centrality
    betweenness_centrality = nx.betweenness_centrality(G)
    degree_centrality = nx.degree_centrality(G)
    degree_centrality_drug = [{node:centrality} for node, centrality in degree_centrality.items() if node[0]=="*"]
    degree_centrality_gene = [{node:centrality} for node, centrality in degree_centrality.items() if node[0]=="@"]
    betweenness_centrality_drug = [{node:centrality} for node, centrality in betweenness_centrality.items() if node[0]=="*"]
    betweenness_centrality_gene = [{node:centrality} for node, centrality in betweenness_centrality.items() if node[0]=="@"]
    return {"degree_centrality_drug":degree_centrality_drug, "degree_centrality_gene":degree_centrality_gene, "betweenness_centrality_drug": betweenness_centrality_drug, "betweenness_centrality_gene": betweenness_centrality_gene}



def get_statistics_by_ONE_atc_for_measure_centralization_drug_disease(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    unique_drug_list = list(Drug.objects.filter(drug_bankID__in=undup_drugs).values_list("name", flat=True))
    unique_drug_list2 = ["*"+ d for d in unique_drug_list]
    G = nx.Graph()
    #adding nodes
    G.add_nodes_from(unique_drug_list2)
    associations = list(DrugDiseaseStudy.objects.filter(drug_bankID__name__in=unique_drug_list).values_list("disease_name__disease_name", flat=True))
    associations2 = ["#"+ d for d in list(set(associations))]
    G.add_nodes_from(associations2)

    #adding edges
    for drug in unique_drug_list:
        disease_names = list(DrugDiseaseStudy.objects.filter(drug_bankID__name=drug).values_list("disease_name__disease_name", flat=True))
        for disease_name in disease_names:
            G.add_edge("*"+drug, "#"+disease_name)
    
    #calculate centrality
    betweenness_centrality = nx.betweenness_centrality(G)
    degree_centrality = nx.degree_centrality(G)
    degree_centrality_drug = [{node:centrality} for node, centrality in degree_centrality.items() if node[0]=="*"]
    degree_centrality_disease = [{node:centrality} for node, centrality in degree_centrality.items() if node[0]=="#"]
    betweenness_centrality_drug = [{node:centrality} for node, centrality in betweenness_centrality.items() if node[0]=="*"]
    betweenness_centrality_disease = [{node:centrality} for node, centrality in betweenness_centrality.items() if node[0]=="#"]
    return {"degree_centrality_drug":degree_centrality_drug, "degree_centrality_disease":degree_centrality_disease, "betweenness_centrality_drug": betweenness_centrality_drug, "betweenness_centrality_disease": betweenness_centrality_disease}

def get_statistics_by_atc_for_measure_centralization_drug_disease(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_statistics_by_atc_for_measure_centralization_drug_disease_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_statistics_by_atc_for_measure_centralization_drug_disease_"+atc_code+"_"+atc_comparison)
    else:
        response_data = {
            "atc_code":get_statistics_by_ONE_atc_for_measure_centralization_drug_disease(atc_code), 
            "atc_comparison":get_statistics_by_ONE_atc_for_measure_centralization_drug_disease(atc_comparison), 
            
        }
        cache.set("get_statistics_by_atc_for_measure_centralization_drug_disease_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)


def get_data_for_comparing_network_associate_distribution(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_data_for_comparing_network_association_distribution_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_data_for_comparing_network_association_distribution_"+atc_code+"_"+atc_comparison)
    else:
        response_data = {
            "atc_code_classes":get_data_for_ONE_atc_code_for_comparing_network_association_distribution(atc_code).get("classes"), 
            "atc_comparison_classes":get_data_for_ONE_atc_code_for_comparing_network_association_distribution(atc_comparison).get("classes"), 
            "atc_code_class_count":get_data_for_ONE_atc_code_for_comparing_network_association_distribution(atc_code).get("class_count"), 
            "atc_comparison_class_count":get_data_for_ONE_atc_code_for_comparing_network_association_distribution(atc_comparison).get("class_count"), 
        }
        cache.set("get_data_for_comparing_network_association_distribution_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_data_for_ONE_atc_code_for_comparing_network_association_distribution(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
    distribution = []
    for drug in drug_objs:
        associations = DrugDiseaseStudy.objects.filter(drug_bankID=drug).values_list("disease_name", flat=True)
        distribution.append(len(list(associations)))
    
    # Count each value
    distribution = Counter(distribution)
    # Sort the keys of the counter
    distribution = dict(sorted(distribution.items()))
    
    response_data = {
        "classes": list(distribution.keys()), 
        "class_count": list(distribution.values()), 
    }
    return response_data

def get_data_for_comparing_network_degree_distribution(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison")
    if cache.get("get_data_for_comparing_network_degree_distribution_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_data_for_comparing_network_degree_distribution_"+atc_code+"_"+atc_comparison)
    else:
        response_data = {
            "atc_code_classes":get_data_for_ONE_atc_code_for_comparing_network_degree_distribution(atc_code).get("classes"), 
            "atc_code_class_count":get_data_for_ONE_atc_code_for_comparing_network_degree_distribution(atc_code).get("class_count"), 
            "atc_comparison_classes":get_data_for_ONE_atc_code_for_comparing_network_degree_distribution(atc_comparison).get("classes"), 
            "atc_comparison_class_count":get_data_for_ONE_atc_code_for_comparing_network_degree_distribution(atc_comparison).get("class_count"), 
            # "both": {
            #     "distribution": get_data_for_ONE_atc_code_for_comparing_network_degree_distribution(atc_code).get("distribution") + get_data_for_ONE_atc_code_for_comparing_network_degree_distribution(atc_comparison).get("distribution"), 
            # }
        }
        cache.set("get_data_for_comparing_network_degree_distribution_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_data_for_ONE_atc_code_for_comparing_network_degree_distribution(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    
    drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
    distribution = []
    for drug in drug_objs:
        interactions = Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID", flat=True)
        distribution.append(len(list(interactions)))
    distribution = Counter(distribution)
    distribution = dict(sorted(distribution.items()))
    response_data = {
        "classes": list(distribution.keys()), 
        "class_count": list(distribution.values()), 
    }
    print(atc_code , " undup_drugs ", undup_drugs, " response_data ", response_data)
    return response_data

def get_data_for_comparing_common_and_unique_network_element(request):
    atc_code = request.GET.get("atc_code")
    atc_comparison = request.GET.get("atc_comparison") #compare
    if cache.get("get_data_for_comparing_common_and_unique_network_element_"+atc_code+"_"+atc_comparison):
        response_data = cache.get("get_data_for_comparing_common_and_unique_network_element_"+atc_code+"_"+atc_comparison)
    else:
        atc_code_data = get_data_ONE_atc_code_for_comparing_common_and_unique_network_element(atc_code)
        atc_comparison_data = get_data_ONE_atc_code_for_comparing_common_and_unique_network_element(atc_comparison)
        response_data ={
        "atc_code": atc_code,
        "atc_comparison": atc_comparison,
        "common_drugs": [d for d in atc_code_data.get("drug_objs") if d in atc_comparison_data.get("drug_objs")],
        "common_proteins": [d for d in atc_code_data.get("protein_objs") if d in atc_comparison_data.get("protein_objs")],
        "common_diseases": [d for d in atc_code_data.get("disease_objs") if d in atc_comparison_data.get("disease_objs")],
        "unique_drug_atc_code": [d for d in atc_code_data.get("drug_objs") if not d in atc_comparison_data.get("drug_objs")],
        "unique_protein_atc_code": [d for d in atc_code_data.get("protein_objs") if not d in atc_comparison_data.get("protein_objs")],
        "unique_disease_atc_code": [d for d in atc_code_data.get("disease_objs") if not d in atc_comparison_data.get("disease_objs")],
        "unique_drug_atc_comparison": [d for d in atc_comparison_data.get("drug_objs") if not d in atc_code_data.get("drug_objs")],
        "unique_protein_atc_comparison": [d for d in atc_comparison_data.get("protein_objs") if not d in atc_code_data.get("protein_objs")],
        "unique_disease_atc_comparison": [d for d in atc_comparison_data.get("disease_objs") if not d in atc_code_data.get("disease_objs")],
        }
        cache.set("get_data_for_comparing_common_and_unique_network_element_"+atc_code+"_"+atc_comparison, response_data, 60*60)
    return JsonResponse(response_data)

def get_data_ONE_atc_code_for_comparing_common_and_unique_network_element(atc_code):
    allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
    chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
    drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
    undup_drugs = list(set(drugs))
    drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
    protein_objs = []
    disease_objs = []
    for drug in drug_objs:
        #drug-protein interaction
        interactions = Interaction.objects.filter(drug_bankID=drug)
        protein_objs += list(interactions.values_list('uniprot_ID', flat=True))
        #drug-disease association
        association = DrugDiseaseStudy.objects.filter(drug_bankID=drug)
        disease_objs += list(association.values_list('disease_name', flat=True))

    protein_objs = list(set(protein_objs))
    disease_objs = list(set(disease_objs))
    response_data = {
        "drug_objs": list(drug_objs.values_list("drug_bankID", flat=True)),
        "protein_objs": protein_objs,
        "disease_objs": list(set(DrugDiseaseStudy.objects.filter(disease_name__in=disease_objs).values_list("disease_name__disease_name", flat=True))),
    }
    return response_data

def get_statistics_by_atc_for_network_size_comparison(request):
    atc_code = request.GET.get("atc_code") # main
    atc_comparison = request.GET.get("atc_comparison") #compare
    response_data ={
        "atc_code": get_statistics_by_ONE_atc_for_network_size_comparison(atc_code),
        "atc_comparison": get_statistics_by_ONE_atc_for_network_size_comparison(atc_comparison)
    }
    return JsonResponse(response_data)

# helper
def get_statistics_by_ONE_atc_for_network_size_comparison(atc_code):
    if cache.get("get_statistics_by_ONE_atc_for_network_size_comparison_"+atc_code):
        response_data = cache.get("get_statistics_by_ONE_atc_for_network_size_comparison_"+atc_code)
    else:
        allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
        drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
        undup_drugs = list(set(drugs))
        drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
        interaction_all = []
        association_all = []
        protein_objs = []
        disease_objs = []
        for drug in drug_objs:
            #drug-protein interaction
            interactions = Interaction.objects.filter(drug_bankID=drug)
            interaction_all+=interactions
            protein_objs += list(interactions.values_list('uniprot_ID', flat=True))
            #drug-disease association
            association = DrugDiseaseStudy.objects.filter(drug_bankID=drug)
            association_all+=association
            disease_objs += list(association.values_list('disease_name', flat=True))
        protein_count = len(list(set(protein_objs)))
        disease_count = len(list(set(disease_objs)))
        response_data = {
            "name_atc_code": atc_code,
            "no_of_drugs": len(drug_objs),
            "no_of_diseases": disease_count,
            "no_of_proteins": protein_count,
            "NoOfDrugPoteinInteractions": len(interaction_all),
            "NoOfDrugDiseaseAssociationStudy": len(association_all),
        }
        cache.set("get_statistics_by_ONE_atc_for_network_size_comparison_"+atc_code, response_data, 60*60)
    return response_data

def get_statistics_by_atc(request):
    atc_code = request.GET.get("atc_code")
    if cache.get("get_statistics_by_atc_"+atc_code):
        response_data = cache.get("get_statistics_by_atc_"+atc_code)
    else:
        allChemicalSubstanceCodes = list(DrugAtcAssociation.objects.all().values_list("atc_id", flat=True))
        chemicalSubstanceCodesFiltered = [c for c in allChemicalSubstanceCodes if c.startswith(atc_code)]
        drugs = DrugAtcAssociation.objects.filter(atc_id__in=chemicalSubstanceCodesFiltered).select_related('drug_id').values_list("drug_id", flat=True)
        undup_drugs = list(set(drugs))
        drug_objs = Drug.objects.filter(drug_bankID__in=undup_drugs).order_by('name')
        interaction_all = []
        association_all = []
        for drug in drug_objs:
            #drug-protein interaction
            interactions = Interaction.objects.filter(drug_bankID=drug)
            interaction_all+=interactions
            #drug-disease association
            association = DrugDiseaseStudy.objects.filter(drug_bankID=drug)
            association_all+=association
        interaction_all = list(set(interaction_all))
        association_all = list(set(association_all))

        noOfTargetTypes = len([interaction for interaction in interaction_all if interaction.interaction_type=="target" ])
        noOfTransporterTypes = len([interaction for interaction in interaction_all if interaction.interaction_type=="transporter" ])
        noOfCarrierTypes = len([interaction for interaction in interaction_all if interaction.interaction_type=="carrier" ])
        noOfEnzymeTypes = len([interaction for interaction in interaction_all if interaction.interaction_type=="enzyme" ])

        #0 -> Nutraceutical, 1 - Experimental, 2- Investigational, 3- Approved , 4 - Vet approved, 5 - Illicit
        noOfNutraceuticalDrug = len([drug for drug in drug_objs if drug.Clinical_status==0])
        noOfExperimentalDrug = len([drug for drug in drug_objs if drug.Clinical_status==1])
        noOfInvestigationalDrug = len([drug for drug in drug_objs if drug.Clinical_status==2])
        noOfApprovedDrug = len([drug for drug in drug_objs if drug.Clinical_status==3])
        noOfVetApprovedDrug = len([drug for drug in drug_objs if drug.Clinical_status==4])
        noOfIllicitDrug = len([drug for drug in drug_objs if drug.Clinical_status==5])
        noOfIllicitDrug = len([drug for drug in drug_objs if drug.Clinical_status==5])
        noOfSmallMolecule = len([drug for drug in drug_objs if drug.drugtype.type_detail=="Small Molecule"])
        noOfBiotech = len([drug for drug in drug_objs if drug.drugtype.type_detail=="Biotech"])

        noOfPhase1 = len([s for s in association_all if s.clinical_trial=="1"])
        noOfPhase2 = len([s for s in association_all if s.clinical_trial=="2"])
        noOfPhase3 = len([s for s in association_all if s.clinical_trial=="3"])
        noOfPhase4 = len([s for s in association_all if s.clinical_trial=="4"])

        disease_classes = list(Disease.objects.values_list('disease_class', flat=True).distinct())
        new_disease_classes = []
        disease_class_count = []
        response_data = {
            "no of drugs": len(drug_objs),
            "atc_code": atc_code,
            "NoOfAllInteractions": len(interaction_all),
            "NoOfTargetTypes": noOfTargetTypes, 
            "NoOfTransporterTypes": noOfTransporterTypes, 
            "NoOfCarrierTypes": noOfCarrierTypes, 
            "NoOfEnzymeTypes": noOfEnzymeTypes, 
            "NoOfNutraceuticalDrug": noOfNutraceuticalDrug,
            "NoOfExperimentalDrug": noOfExperimentalDrug,
            "NoOfInvestigationalDrug":noOfInvestigationalDrug,
            "NoOfApprovedDrug": noOfApprovedDrug,
            "NoOfVetApprovedDrug": noOfVetApprovedDrug,
            "NoOfIllicitDrug":noOfIllicitDrug,
            "NoOfSmallMolecule":noOfSmallMolecule,
            "NoOfBiotech":noOfBiotech,
            "noOfPhase1": noOfPhase1,
            "noOfPhase2": noOfPhase2,
            "noOfPhase3": noOfPhase3,
            "noOfPhase4": noOfPhase4,
            "totalNoOfDisease": noOfPhase1 + noOfPhase2 + noOfPhase3 + noOfPhase4,
            }
        for dc in disease_classes:
            c = DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=undup_drugs) & Q(disease_name__disease_class=dc)).distinct().count()
            if c>0:
                disease_class_count.append(c)
                new_disease_classes.append(dc)
        response_data["disease_classes"]=new_disease_classes
        response_data["disease_class_count"]=disease_class_count

        cache.set("get_statistics_by_atc_"+atc_code, response_data, 60*60)
    return JsonResponse(response_data)

#this is a helper function, not a view
def get_network_statistics_by_drug(drug_id):
    if cache.get("get_network_statistics_by_drug_"+drug_id):
        data = cache.get("get_network_statistics_by_drug_"+drug_id)
    else:
        interactions = Interaction.objects.filter(drug_bankID=drug_id)
        noOfTargetTypes = len([interaction for interaction in interactions if interaction.interaction_type=="target" ])
        noOfTransporterTypes = len([interaction for interaction in interactions if interaction.interaction_type=="transporter" ])
        noOfCarrierTypes = len([interaction for interaction in interactions if interaction.interaction_type=="carrier" ])
        noOfEnzymeTypes = len([interaction for interaction in interactions if interaction.interaction_type=="enzyme" ])
        drug = Drug.objects.get(drug_bankID=drug_id)

        noOfNutraceuticalDrug = int(drug.Clinical_status == 0)
        noOfExperimentalDrug = int(drug.Clinical_status == 1)
        noOfInvestigationalDrug = int(drug.Clinical_status == 2)
        noOfApprovedDrug = int(drug.Clinical_status == 3)
        noOfVetApprovedDrug = int(drug.Clinical_status == 4)
        noOfIllicitDrug = int(drug.Clinical_status == 5)
        noOfSmallMolecule = int(drug.drugtype.type_detail=="Small Molecule")
        noOfBiotech = int(drug.drugtype.type_detail=="Biotech")

        data = {
            "NoOfTargetTypes": noOfTargetTypes, 
            "NoOfTransporterTypes": noOfTransporterTypes, 
            "NoOfCarrierTypes": noOfCarrierTypes, 
            "NoOfEnzymeTypes": noOfEnzymeTypes, 
            "NoOfNutraceuticalDrug": noOfNutraceuticalDrug,
            "NoOfExperimentalDrug": noOfExperimentalDrug,
            "NoOfInvestigationalDrug":noOfInvestigationalDrug,
            "NoOfApprovedDrug": noOfApprovedDrug,
            "NoOfVetApprovedDrug": noOfVetApprovedDrug,
            "NoOfIllicitDrug":noOfIllicitDrug,
            "NoOfSmallMolecule":noOfSmallMolecule,
            "NoOfBiotech":noOfBiotech,
            }
        cache.set("get_network_statistics_by_drug_"+drug_id, data, 60*60)
    return data

def get_drug_association(request):
    drug_id = request.GET.get("drug_id")
    try:
        drug = Drug.objects.get(drug_bankID=drug_id)
    except Drug.DoesNotExist:
        raise Http404("Drug does not exist")
    associations_list = [
        {"drug_bankID": drug_id, "name": drug.name, "description": drug.description, "target_list": [ {"genename": item.uniprot_ID.genename, "gene_id": item.uniprot_ID.geneID, "uniProt_ID": item.uniprot_ID.uniprot_ID, "count_drug": len(Interaction.objects.filter(uniprot_ID=item.uniprot_ID))} for item in Interaction.objects.filter(drug_bankID=drug_id)]}
        ]
    drug_disease_study_list = [{"disease_name": study.disease_name.disease_name, "clinical_trial": study.clinical_trial, "disease_class": study.disease_name.disease_name} for study in DrugDiseaseStudy.objects.filter(drug_bankID=drug_id)]
    data = get_network_statistics_by_drug(drug_id)
    total_interaction = 0
    interacted_protein = []
    for association in associations_list:
            total_interaction+=len(association.get("target_list"))
            for target in association.get("target_list"):
                interacted_protein.append(target.get("uniProt_ID"))
    interacted_protein = list(set(interacted_protein))
    gene_based_burden_data = get_genebased_data_from_genebass_by_drug(drug_id)
    pgx_clinical_data = _get_clinical_pgx_data_by_drug(drug_id)
    response_data = {
        "drug_id":drug_id,
        "associations": associations_list,
        "total_interaction": total_interaction,
        "no_of_interacted_protein": len(interacted_protein),
        "atc_code": "no ATC code",
        "NoOfTargetTypes": data.get("NoOfTargetTypes"), 
        "NoOfTransporterTypes": data.get("NoOfTransporterTypes"), 
        "NoOfCarrierTypes": data.get("NoOfCarrierTypes"), 
        "NoOfEnzymeTypes": data.get("NoOfEnzymeTypes"), 
        "NoOfNutraceuticalDrug": data.get("NoOfNutraceuticalDrug"),
        "NoOfExperimentalDrug": data.get("NoOfExperimentalDrug"),
        "NoOfInvestigationalDrug": data.get("NoOfInvestigationalDrug"),
        "NoOfApprovedDrug": data.get("NoOfApprovedDrug"),
        "NoOfVetApprovedDrug": data.get("NoOfVetApprovedDrug"),
        "NoOfIllicitDrug": data.get("NoOfIllicitDrug"),
        "NoOfSmallMolecule": data.get("NoOfSmallMolecule"),
        "NoOfBiotech": data.get("NoOfBiotech"),
        "gene_based_burden_data": gene_based_burden_data,
        "pgx_clinical_data": pgx_clinical_data,
    }

    return JsonResponse(response_data)


def get_drug_list_by_uniprotID(request):
    uniprot_ID = request.GET.get("uniProt_ID")
    genename = Protein.objects.get(uniprot_ID=uniprot_ID).genename
    interactions = Interaction.objects.filter(uniprot_ID=uniprot_ID)
    noOfTargetTypes = len([interaction for interaction in interactions if interaction.interaction_type=="target" ])
    noOfTransporterTypes = len([interaction for interaction in interactions if interaction.interaction_type=="transporter" ])
    noOfCarrierTypes = len([interaction for interaction in interactions if interaction.interaction_type=="carrier" ])
    noOfEnzymeTypes = len([interaction for interaction in interactions if interaction.interaction_type=="enzyme" ])
    #0 -> Nutraceutical, 1 - Experimental, 2- Investigational, 3- Approved , 4 - Vet approved, 5 - Illicit

    noOfNutraceuticalDrug = len([interaction for interaction in interactions if interaction.drug_bankID.Clinical_status==0])
    noOfExperimentalDrug = len([interaction for interaction in interactions if interaction.drug_bankID.Clinical_status==1])
    noOfInvestigationalDrug = len([interaction for interaction in interactions if interaction.drug_bankID.Clinical_status==2])
    noOfApprovedDrug = len([interaction for interaction in interactions if interaction.drug_bankID.Clinical_status==3])
    noOfVetApprovedDrug = len([interaction for interaction in interactions if interaction.drug_bankID.Clinical_status==4])
    noOfIllicitDrug = len([interaction for interaction in interactions if interaction.drug_bankID.Clinical_status==5])
    noOfIllicitDrug = len([interaction for interaction in interactions if interaction.drug_bankID.Clinical_status==5])
    noOfSmallMolecule = len([interaction for interaction in interactions if interaction.drug_bankID.drugtype.type_detail=="Small Molecule"])
    noOfBiotech = len([interaction for interaction in interactions if interaction.drug_bankID.drugtype.type_detail=="Biotech"])
    temp = {
        "Target": uniprot_ID,
        "Genename": genename,
        "NoOfDrugs": len(interactions),
        "ListOfDrugIDs": [interaction.drug_bankID.drug_bankID for interaction in interactions],
        "ListOfDrugNames": [interaction.drug_bankID.name for interaction in interactions],
        "NoOfTargetTypes": noOfTargetTypes, 
        "NoOfTransporterTypes": noOfTransporterTypes, 
        "NoOfCarrierTypes": noOfCarrierTypes, 
        "NoOfEnzymeTypes": noOfEnzymeTypes, 
        "NoOfNutraceuticalDrug": noOfNutraceuticalDrug,
        "NoOfExperimentalDrug": noOfExperimentalDrug,
        "NoOfInvestigationalDrug":noOfInvestigationalDrug,
        "NoOfApprovedDrug": noOfApprovedDrug,
        "NoOfVetApprovedDrug": noOfVetApprovedDrug,
        "NoOfIllicitDrug":noOfIllicitDrug,
        "NoOfSmallMolecule":noOfSmallMolecule,
        "NoOfBiotech":noOfBiotech,

    }
    return JsonResponse({ "response_data" : temp})
   


def retrieving_anatomical_group(atc_code):
    return list(AtcAnatomicalGroup.objects.filter(id__iexact=atc_code).values('id', 'name'))


def retrieving_therapeutic_group(atc_code):
    return list(AtcTherapeuticGroup.objects.filter(id__startswith=atc_code).values('id', 'name'))


def retrieving_pharmacological_group(atc_code):
    return list(AtcPharmacologicalGroup.objects.filter(id__startswith=atc_code).values('id', 'name'))


def retrieving_chemical_group(atc_code):
    return list(AtcChemicalGroup.objects.filter(id__startswith=atc_code).values('id', 'name'))


def retrieving_chemical_substance(atc_code):
    return list(AtcChemicalSubstance.objects.filter(id__startswith=atc_code).values('id', 'name'))


# def get_atc_sub_levels(request):
#     atc_code = request.GET.get("atc_code");
#     data = {'atc_code': atc_code}
#     if len(atc_code) == 1:
#         data = {"anatomical_group": retrieving_anatomical_group(atc_code),
#                 "therapeutic_group": retrieving_therapeutic_group(atc_code),
#                 "pharmacological_group": retrieving_pharmacological_group(atc_code),
#                 "chemical_group": retrieving_chemical_group(atc_code),
#                 "chemical_substance": retrieving_chemical_substance(atc_code)}
#     if len(atc_code) == 3:
#         data = {"therapeutic_group": retrieving_therapeutic_group(atc_code),
#                 "pharmacological_group": retrieving_pharmacological_group(atc_code),
#                 "chemical_group": retrieving_chemical_group(atc_code),
#                 "chemical_substance": retrieving_chemical_substance(atc_code)}
#     if len(atc_code) == 4:
#         data = {"pharmacological_group": retrieving_pharmacological_group(atc_code),
#                 "chemical_group": retrieving_chemical_group(atc_code),
#                 "chemical_substance": retrieving_chemical_substance(atc_code)}
#     if len(atc_code) == 5:
#         data = {"chemical_group": retrieving_chemical_group(atc_code),
#                 "chemical_substance": retrieving_chemical_substance(atc_code)}
#     if len(atc_code) == 7:
#         data = {"chemical_substance": retrieving_chemical_substance(atc_code)}

#     # re-organize the data
#     reorganized_data = {}

#     # Loop through each element in the original data
#     for group_type, group_list in data.items():
#         # Create a dictionary to hold the grouped elements
#         grouped_elements = {}

#         # Loop through the elements in the group_list
#         for element in group_list:
#             # Extract the element ID
#             element_id = element['id']

#             # Add the element to the grouped_elements dictionary
#             grouped_elements[element_id] = element

#         # Add the grouped_elements to the reorganized_data using the group_type as the key
#         reorganized_data[group_type] = grouped_elements
#     reorganized_data["atc_code"] = atc_code
#     reorganized_data["data"] = data
#     return JsonResponse(reorganized_data, safe=False)

def get_atc_sub_levels(request):
    atc_code = request.GET.get("atc_code");
    data = {'atc_code': atc_code}
    if len(atc_code) == 1:
        data = {
                "therapeutic_group": list(AtcTherapeuticGroup.objects.filter(id__startswith=atc_code).values('id', "name")),
                "pharmacological_group": list(AtcPharmacologicalGroup.objects.filter(id__startswith=atc_code).values('id')),
                "chemical_group": list(AtcChemicalGroup.objects.filter(id__startswith=atc_code).values('id', "name")),
                "chemical_substance": list(AtcChemicalSubstance.objects.filter(id__startswith=atc_code).values('id', "name"))}
    if len(atc_code) == 3:
        data = {
                "pharmacological_group": list(AtcPharmacologicalGroup.objects.filter(id__startswith=atc_code).values('id', "name")),
                "chemical_group": list(AtcChemicalGroup.objects.filter(id__startswith=atc_code).values('id', "name")),
                "chemical_substance": list(AtcChemicalSubstance.objects.filter(id__startswith=atc_code).values('id', "name"))}
    if len(atc_code) == 4:
        data = {
                "chemical_group": list(AtcChemicalGroup.objects.filter(id__startswith=atc_code).values('id', "name")),
                "chemical_substance": list(AtcChemicalSubstance.objects.filter(id__startswith=atc_code).values('id', "name"))}
    if len(atc_code) == 5:
        data = {
                "chemical_substance": list(AtcChemicalSubstance.objects.filter(id__startswith=atc_code).values('id', "name"))}
    if len(atc_code) == 7:
        data = {"chemical_substance": list(AtcChemicalSubstance.objects.filter(id__iexact=atc_code).values('id', "name"))}
    
    temp=[]
    for key in data.keys():
        temp+=[item for item in data.get(key)]
    return JsonResponse({"atc_code": atc_code, "sub_atc_codes": temp}, safe=False)


class DrugByAtcBaseView:
    def get_drug_by_atc_code(self, slug):

        context = {}
        if slug is not None:
            if cache.get("drugs_by_atc_data_" + slug) is not None:
                table = cache.get("drugs_by_atc_data_" + slug)
            else:
                list_of_drugs = []
                data = {"chemical_substance": retrieving_chemical_substance(slug)}
                for value in data.get('chemical_substance'):
                    chemical_substance_code = value.get("id")
                    drug_ids = DrugAtcAssociation.objects.filter(
                        atc_id=chemical_substance_code).values_list("drug_id", flat=True)
                    for drug_id in drug_ids:
                        items = Drug.objects.filter(drug_bankID=drug_id)
                        if len(items)>0:
                            drug = items.first()
                            temp = {
                                    "DrugbankID": drug.drug_bankID,
                                    "drugname": drug.name,
                                    }
                            list_of_drugs.append(temp)
                context = dict()
                cache.set("drugs_by_atc_data_" + slug, list_of_drugs, 60 * 60)
            context['list_of_drugs'] = list_of_drugs
        return context
    
def retrieving_atc_description(atc_code):
    if len(atc_code)==1:
        return AtcAnatomicalGroup.objects.get(id__iexact=atc_code)
    else:
        if len(atc_code)==3:
            return AtcTherapeuticGroup.objects.get(id__iexact=atc_code)
        else:
            if len(atc_code)==4:
                return AtcPharmacologicalGroup.objects.get(id__iexact=atc_code)
            else:
                if len(atc_code)==5:
                    return AtcChemicalGroup.objects.get(id__iexact=atc_code)
                else:
                    return AtcChemicalSubstance.objects.get(id__iexact=atc_code)


class DescriptionByAtcBaseView:
    def get_description_by_atc_code(self, slug):
        context = {}
        if slug is not None:
            if cache.get("description_by_atc_data_" + slug) is not None:
                description = cache.get("description_by_atc_data_" + slug)
            else:
                description = retrieving_atc_description(slug)
                context = dict()
                cache.set("description_by_atc_data_" + slug, description, 60 * 60)
            context['description'] = description
        return context

def retrieving_atc_description(atc_code):
    rs = ""
    if len(atc_code)==1:
        rs = list(AtcAnatomicalGroup.objects.filter(id=atc_code).values_list("name", flat=True))
    else:
        if len(atc_code)==3:
            rs = list(AtcTherapeuticGroup.objects.filter(id=atc_code).values_list("name", flat=True))
        else:
            if len(atc_code)==4:
                rs = list(AtcPharmacologicalGroup.objects.filter(id=atc_code).values_list("name", flat=True))
            else:
                if len(atc_code)==5:
                    rs = list(AtcChemicalGroup.objects.filter(id=atc_code).values_list("name", flat=True))
                else:
                    if len(atc_code)==7:
                        rs = list(AtcChemicalSubstance.objects.filter().values_list("name", flat=True))

    if len(rs)==1:
            return rs[0]
    else:
            return "Wrong Atc code"


def retrieving_atc_sublevel(level):
    if level.lower()=="a":
        return list(AtcAnatomicalGroup.objects.all().values_list("id", "name"))
    else:
        if level.lower()=="t":
            return list(AtcTherapeuticGroup.objects.all().values_list("id", "name"))
        else:
            if level.lower()=="p":
                return list(AtcPharmacologicalGroup.objects.all().values_list("id", "name"))
            else:
                if level.lower()=="c":
                    return list(AtcChemicalGroup.objects.all().values_list("id", "name"))
                else:
                    if level.lower()=="cs":
                        return list(AtcChemicalSubstance.objects.all().values_list("id", "name"))
                    else:
                        return []

class AtcCodesByLevelBaseView:
    def get_atc_codes_by_level(self, slug):
        context = {}
        if slug is not None:
            if cache.get("atc_codes_by_level_" + slug) is not None:
                list_of_codes = cache.get("atc_codes_by_level_" + slug)
            else:
                list_of_codes = retrieving_atc_sublevel(slug)
                context = dict()
                cache.set("atc_codes_by_level_" + slug, list_of_codes, 60 * 60)
            context['list_of_codes'] = list_of_codes
        return context
    
class TargetsByDrugBaseView:
    def get_targets_by_drug(self, slug):
        context = {}
        if slug is not None:
            if cache.get("targets_by_drug_" + slug) is not None:
                list_of_targets = cache.get("targets_by_drug_" + slug)
            else:
                list_of_targets_id = Interaction.objects.filter(drug_bankID = slug).values_list("uniprot_ID", flat=True)
                list_of_targets = Protein.objects.filter(uniprot_ID__in=list_of_targets_id).values_list("uniprot_ID", "protein_name", "geneID", "genename")
                context = dict()
                cache.set("targets_by_drug_" + slug, list_of_targets, 60 * 60)
            context['list_of_targets'] = list_of_targets
        return context
    
class AtcCodesByDrugView:
    def get_atc_codes_by_drug(self, slug):
        context = {}
        if slug is not None:
            if cache.get("atc_codes_by_drug_" + slug) is not None:
                returned_data = cache.get("atc_codes_by_drug_" + slug)
            else:
                list_of_atc_codes = list(DrugAtcAssociation.objects.filter(
                        drug_id=slug).values_list("atc_id"))
                returned_data = []
                for code in list_of_atc_codes:
                    name = AtcChemicalSubstance.objects.get(id=code[0]).name
                    returned_data.append({"Atc code": code, "Description": name })

                context = dict()
                cache.set("atc_codes_by_drug_" + slug, returned_data, 60 * 60)
            context['list_of_atc_codes'] = returned_data
        return context
    

class PGxByAtcCodeView:
    def get_pharmgkb_pgx_by_atc_code(self, slug):
        context = {}
        if slug is not None:
            if cache.get("pgx_by_atc_codes_" + slug) is not None:
                returned_data = cache.get("pgx_by_atc_codes_" + slug)
            else:
                drug_ids = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__icontains=slug).values_list("drug_id", flat=True))))
                pgx = Pharmgkb.objects.filter(drugbank_id__in=drug_ids)
                returned_data = []
                for row in pgx:
                    drug_id = row.drugbank_id.drug_bankID
                    r = {
                            "DrugbankID": drug_id,
                            "Drugname": Drug.objects.get(drug_bankID=drug_id).name,
                            "Variant_or_Haplotypes": row.Variant_or_Haplotypes,
                            "PMID": row.PMID,
                            "Phenotype_Category": row.Phenotype_Category,
                            "Significance": row.Significance,
                            "Notes": row.Notes,
                            "Sentence": row.Sentence,
                            "Alleles": row.Alleles,
                            "P_Value": row.P_Value,
                            "Biogeographical_Groups": row.Biogeographical_Groups,
                            "Study_Type": row.Study_Type,
                            # "Study_Cases": row.Study_Cases,
                            # "Study_Controls": row.Study_Controls,
                            "Direction_of_effect": row.Direction_of_effect,
                            "PD_PK_terms": row.PD_PK_terms,
                            "Metabolizer_types": row.Metabolizer_types,
                        }
                    returned_data.append(r)

                context = dict()
                cache.set("pgx_by_atc_codes_" + slug, returned_data, 60 * 60)
            context['pgx'] = returned_data
        return context
    
class DrugTargetInteractionByAtcBaseView:
    def get_interaction_by_atc_code(self, slug):
        context = {}
        if slug is not None:
            if cache.get("interactions_by_atc_code_" + slug) is not None:
                returned_data = cache.get("interactions_by_atc_code_" + slug)
            else:
                drug_ids = DrugAtcAssociation.objects.filter(atc_id__id__istartswith=slug).values_list("drug_id", flat=True)
                returned_data = []
                for drug_id in drug_ids:
                    interactions = Interaction.objects.filter(drug_bankID=drug_id).values_list("uniprot_ID", "actions", "known_action", "interaction_type")
                    for interaction in interactions:
                        temp={
                            "drug_bankID":drug_id,
                            "uniprot_ID":interaction[0],
                            "actions":interaction[1],
                            "known_action":interaction[2],
                            "interaction_type":interaction[3],
                        }
                        returned_data.append(temp)
                context = dict()
                cache.set("interactions_by_atc_code_" + slug, returned_data, 60 * 60)
            context['interactions_by_atc_code'] = returned_data
        return context
    
class DrugDiseaseAssociationByAtcBaseView:
    def get_association_by_atc_code(self, slug):
        context = {}
        if slug is not None:
            if cache.get("associations_by_atc_code_" + slug) is not None:
                returned_data = cache.get("associations_by_atc_code_" + slug)
            else:
                drug_ids = DrugAtcAssociation.objects.filter(atc_id__id__istartswith=slug).values_list("drug_id", flat=True)
                returned_data = []
                for drug_id in drug_ids:
                    associations = DrugDiseaseStudy.objects.filter(drug_bankID=drug_id).values_list("disease_name__disease_name", "disease_name__disease_class", "clinical_trial", "link", "standard_inchiKey")
                    drug_name = Drug.objects.get(drug_bankID=drug_id).name
                    for association in associations:
                        temp={
                            "drug_bankID":drug_id,
                            "drug_name": drug_name,
                            "disease_name":association[0],
                            "disease_class":association[1],
                            "clinical_trial":association[2],
                            "link":association[3],
                            "standard_inchiKey":association[4],
                        }
                        returned_data.append(temp)
                context = dict()
                cache.set("associations_by_atc_code_" + slug, returned_data, 60 * 60)
            context['associations_by_atc_code'] = returned_data
        return context
    