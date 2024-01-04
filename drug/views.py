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
    AtcChemicalGroup,
    AtcChemicalSubstance,
    AtcPharmacologicalGroup,
    AtcTherapeuticGroup,
    DrugAtcAssociation,
)
from gene.models import Gene
from interaction.models import Interaction
from protein.models import Protein
from variant.models import GenebassVariant, GenebassPGx, GenebassVariantPGx, Variant, Pharmgkb

from .models import (
    Drug,
    DrugAtcAssociation,
)
from .services import DrugNetworkGetDataService, DrugsNetworkGetDataService
from time import perf_counter


app_name = 'drug'


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
    data = DrugNetworkGetDataService(drug=drug).get_general_data()

    return JsonResponse(data, safe=False)

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
        data = DrugsNetworkGetDataService(drug_bank_ids=drug_bank_ids).get_general_data()
        cache.set("drugs_general_data_" + "_".join(drug_bank_ids), data, 60 * 60)

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

    return render(request, 'drug_browser copy.html', {'drugdata': context})


# This is a helper function that takes a request object and checks if it's an AJAX request. It does this by checking if the 'HTTP_X_REQUESTED_WITH' key in the request.META dictionary is set to 'XMLHttpRequest'. If it is, it returns True, otherwise it returns False.
def is_ajax(request):
    return request.META.get('HTTP_X_REQUESTED_WITH') == 'XMLHttpRequest'


def SelectionAutocomplete(request):
    if is_ajax(request=request):

        # This line gets the 'term' parameter from the GET data of the request, removes any leading and trailing whitespace, and assigns the result to the variable 'q'. The 'term' parameter is the search term entered by the user.
        q = request.GET.get('term').strip()
        type_of_selection = request.GET.get('type_of_selection')
        results = []

        if type_of_selection != 'navbar':
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
            # ps4 = Protein.objects.filter(Q(uniprot_ID__icontains=q) | Q(protein_name__icontains=q))
            # if len(ps1) > 0:
            #     redirect = '/drug/'
            #     ps = ps1
            # if len(ps2) > 0:
            #     redirect = "/gene/"
            #     ps = ps2
            # if len(ps3) > 0:
            #     redirect = "/protein/"
            #     ps = ps3

        for p in ps1:
            p_json = {}
            p_json['id'] = p.drug_bankID
            p_json['label'] = p.name
            p_json['type'] = 'drug'
            p_json['redirect'] = '/drug/'
            p_json['category'] = 'Drugs'
            results.append(p_json)

        for p in ps2:
            p_json = {}
            p_json['id'] = p.gene_id
            p_json['type'] = 'Gene'
            p_json['category'] = 'Genes'
            p_json['label'] = p.genename
            p_json['redirect'] = '/gene/'
            results.append(p_json)

        for p in ps3:
            p_json = {}
            p_json['id'] = p.uniprot_ID
            p_json['type'] = 'Protein'
            p_json['category'] = 'Proteins'
            p_json['label'] = p.protein_name
            p_json['redirect'] = '/protein/'
            results.append(p_json)

        # if redirect == '/drug/':
        #     for p in ps:
        #         p_json = {}
        #         p_json['id'] = p.drug_bankID
        #         p_json['label'] = p.name
        #         p_json['type'] = 'drug'
        #         p_json['redirect'] = redirect
        #         p_json['category'] = 'Drugs'
        #         results.append(p_json)
        # else:
        #     if redirect == '/gene/':
        #         for p in ps:
        #             p_json = {}
        #             p_json['id'] = p.gene_id
        #             p_json['type'] = 'Gene'
        #             p_json['category'] = 'Genes'
        #             p_json['label'] = p.genename
        #             p_json['redirect'] = redirect
        #             results.append(p_json)
        #     else:
        #         if redirect == "/protein/":
        #             for p in ps:
        #                 p_json = {}
        #                 p_json['id'] = p.uniprot_ID
        #                 p_json['type'] = 'Protein'
        #                 p_json['category'] = 'Proteins'
        #                 p_json['label'] = p.protein_name
        #                 p_json['redirect'] = redirect
        #                 results.append(p_json)
        data = json.dumps(results)
    else:
        data = 'fail'
    mimetype = 'application/json'
    # return an HTTP response containing the data in JSON format, which is specified by the 'application/json' mimetype
    # JSON format can be understood by the browser and other clients as a JavaScript object. This could be useful if the view is returning data that is meant to be consumed by JavaScript code running on the client side
    return HttpResponse(data, mimetype)


# Create your views here.
def DrugStatistics(request):
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
    print("context = ", context)
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

# @cache_page(LONG_TIMEOUT)
def atc_detail_view(request):
    start_time = perf_counter()
    group_id = request.GET.get('group_id')  # Retrieve group_id from the query parameter
    anatomic_group = None
    try:
        anatomic_group = AtcAnatomicalGroup.objects.get(id=group_id)
    except AtcAnatomicalGroup.DoesNotExist:
        pass

    group_name = anatomic_group.name if anatomic_group else ''

    group2s = AtcTherapeuticGroup.objects.all()
    for group in group2s:
        group.name = format_atc_name(group.name)
    group3s = AtcPharmacologicalGroup.objects.all()
    for group in group3s:
        group.name = format_atc_name(group.name)
    group4s = AtcChemicalGroup.objects.all()
    for group in group4s:
        group.name = format_atc_name(group.name)
    group5s = AtcChemicalSubstance.objects.all()
    for group in group5s:
        group.name = format_atc_name(group.name)
    context = {'group2s': group2s, 'group3s': group3s, 'group4s': group4s, 'group5s': group5s, "group_id": group_id,
               "group_name": group_name}
    end_time = perf_counter()
    print("duration = ", (end_time - start_time))
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
            if len(inp) > 7:
                print("invalid inp")
            else:
                if len(inp) > 5:  # search for id length =7
                    results += list(AtcChemicalSubstance.objects.filter(id__iexact=inp).values('id', 'name'))
                else:
                    if len(inp) == 5:  # search for id length =5
                        results += list(AtcChemicalGroup.objects.filter(id__iexact=inp).values('id', 'name'))
                    else:
                        if len(inp) == 4:  # search for id length =5
                            results += list(
                                AtcPharmacologicalGroup.objects.filter(id__iexact=inp).values('id', 'name'))
                        else:
                            if len(inp) == 3:  # search for id length =5
                                results += list(
                                    AtcTherapeuticGroup.objects.filter(id__iexact=inp).values('id', 'name'))
                            else:
                                results += list(
                                    AtcAnatomicalGroup.objects.filter(id__iexact=inp).values('id', 'name'))
            if query_option == 'containing':
                # Search "name" field in all models
                results += list(AtcAnatomicalGroup.objects.filter(name__icontains=inp).values('id', 'name'))
                results += list(AtcTherapeuticGroup.objects.filter(name__icontains=inp).values('id', 'name'))
                results += list(
                    AtcPharmacologicalGroup.objects.filter(name__icontains=inp).values('id', 'name'))
                results += list(AtcChemicalGroup.objects.filter(name__icontains=inp).values('id', 'name'))
                results += list(AtcChemicalSubstance.objects.filter(name__icontains=inp).values('id', 'name'))

            elif query_option == 'startingwith':
                # Search "id" field in all models
                results += list(AtcAnatomicalGroup.objects.filter(name__istartswith=inp).values('id', 'name'))
                results += list(AtcTherapeuticGroup.objects.filter(name__istartswith=inp).values('id', 'name'))
                results += list(
                    AtcPharmacologicalGroup.objects.filter(name__istartswith=inp).values('id', 'name'))
                results += list(AtcChemicalGroup.objects.filter(name__istartswith=inp).values('id', 'name'))
                results += list(AtcChemicalSubstance.objects.filter(name__istartswith=inp).values('id', 'name'))

        for rs in results:
            rs["name"] = format_atc_name(rs["name"])
        context = {"query_option": query_option, "search_result": results, "input": inp}
        return render(request, 'atc_search_result.html', context)
    print("atc_search_View = ", results)
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

        gene_based_burden_data = get_genebased_data_from_genebass(atc_code)
        pgx_clinical_data = _get_clinical_pgx_data_by_atc(atc_code)
        # Create a JSON response with the data
        response_data = {
            "associations": associations_list,
            "atc_code": atc_code,
            "total_interaction": total_interaction,
            "no_of_interacted_protein":len(interacted_protein),
            "gene_based_burden_data": gene_based_burden_data,
            "pgx_clinical_data": pgx_clinical_data,
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
                                #     print("gene_name", gene_name)
                                #     print("drug_id",drug.drug_bankID)
                                #     print([genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden])
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
    print("_get_clinical_pgx_data_by_atc --> Response data", response_data)          
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
                                    #     print("gene_name", gene_name)
                                    #     print("drug_id",drug.drug_bankID)
                                    #     print([genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden])
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
        print("_get_clinical_pgx_data_by_atc --> Response data", response_data)          
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
                                    #     print("gene_name", gene_name)
                                    #     print("drug_id",drug.drug_bankID)
                                    #     print([genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden])
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
        print("Response data", response_data)          
        if len(response_data)>0:
            cache.set(cache_str, response_data, 60*60)
    # print("finish helper function, response_data = ", response_data)
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
                                    #     print("gene_name", gene_name)
                                    #     print("drug_id",drug.drug_bankID)
                                    #     print([genebass.Pvalue, genebass.Pvalue_Burden, genebass.Pvalue_SKAT, genebass.BETA_Burden, genebass.SE_Burden])
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
    print("finish helper function, response_data = ", response_data)
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
        
        print("genebass_data type: ", type(genebass_data))
        if len(genebass_data) != 0:
            response_data = [{"drug_id": drug_id,
                "interactions": list(Interaction.objects.filter(drug_bankID=drug_id).values("drug_bankID", "uniprot_ID__genename", "interaction_type")),
                "burden_data": list(genebass_data_portion),
                # "burden_data_full": list(genebass_data),
            }]
        if len(response_data)>0:
            print("len response data = ", len(response_data[0].get("burden_data")))
            cache.set("get_variant_based_burden_data_by_drug_"+drug_id, response_data, 60*60)
        else:
            print("no variant pgx data")
    return JsonResponse(response_data, safe=False)


def get_variant_based_burden_data_by_atc(request):
    atc_code = request.GET.get("atc_code")
    print("atc_code = ", atc_code)
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
            print("len response data = ", len(response_data))
            print("len response data item = ", len(response_data[0].get("burden_data")))
            cache.set("get_variant_based_data_by_atc_"+atc_code, response_data, 60*60)
        else:
            print("no variant pgx data")
    return JsonResponse(response_data, safe=False)


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
        for drug in drug_objs:
            interactions = Interaction.objects.filter(drug_bankID=drug)
            interaction_all+=interactions
        interaction_all = list(set(interaction_all))
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
            }
        # print("------get_statistics_by_atc: response_data: ", response_data)
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
    data = get_network_statistics_by_drug(drug_id)
    print("----- inside get_drug_association, data = ", data)
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

    # print("response_data: ", response_data)
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
    # print(" get_drug_list_by_uniprotID - returned data = ", temp)
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


def get_atc_sub_levels(request):
    atc_code = request.GET.get("atc_code");
    data = {'atc_code': atc_code}
    if len(atc_code) == 1:
        data = {"anatomical_group": retrieving_anatomical_group(atc_code),
                "therapeutic_group": retrieving_therapeutic_group(atc_code),
                "pharmacological_group": retrieving_pharmacological_group(atc_code),
                "chemical_group": retrieving_chemical_group(atc_code),
                "chemical_substance": retrieving_chemical_substance(atc_code)}
    if len(atc_code) == 3:
        data = {"therapeutic_group": retrieving_therapeutic_group(atc_code),
                "pharmacological_group": retrieving_pharmacological_group(atc_code),
                "chemical_group": retrieving_chemical_group(atc_code),
                "chemical_substance": retrieving_chemical_substance(atc_code)}
    if len(atc_code) == 4:
        data = {"pharmacological_group": retrieving_pharmacological_group(atc_code),
                "chemical_group": retrieving_chemical_group(atc_code),
                "chemical_substance": retrieving_chemical_substance(atc_code)}
    if len(atc_code) == 5:
        data = {"chemical_group": retrieving_chemical_group(atc_code),
                "chemical_substance": retrieving_chemical_substance(atc_code)}
    if len(atc_code) == 7:
        data = {"chemical_substance": retrieving_chemical_substance(atc_code)}

    # re-organize the data
    reorganized_data = {}

    # Loop through each element in the original data
    for group_type, group_list in data.items():
        # Create a dictionary to hold the grouped elements
        grouped_elements = {}

        # Loop through the elements in the group_list
        for element in group_list:
            # Extract the element ID
            element_id = element['id']

            # Add the element to the grouped_elements dictionary
            grouped_elements[element_id] = element

        # Add the grouped_elements to the reorganized_data using the group_type as the key
        reorganized_data[group_type] = grouped_elements
    reorganized_data["atc_code"] = atc_code
    return JsonResponse(reorganized_data, safe=False)


class TargetByAtcBaseView:
    def get_target_by_atc_code(self, slug):
        # print("checkpoint 1 in get_target_by_atc_code func of TargetByAtcBaseView, self = ", self, " slug = ", slug)

        context = {}
        if slug is not None:
            # print("checkpoint 2 when slug is not None in get_target_by_atc_code func of TargetByAtcBaseView")
            if cache.get("target_by_atc_data_" + slug) is not None:
                table = cache.get("target_by_atc_data_" + slug)
            else:
                # print("checkpoint 3 when not cached in get_target_by_atc_code func of TargetByAtcBaseView")
                table = pd.DataFrame()
                data = {"chemical_substance": retrieving_chemical_substance(slug)}
                for value in data.get('chemical_substance'):
                    chemical_substance_code = value.get("id")
                    drugs = DrugAtcAssociation.objects.filter(
                        atc_id=chemical_substance_code).values_list("drug_id")
                    for drug in drugs:
                        drug_df = pd.DataFrame([drug])
                        table = table.append(drug_df, ignore_index=True)
                table.columns = ["DrugbankID"]
                table.fillna('', inplace=True)
                context = dict()
                cache.set("target_by_atc_data_" + slug, table, 60 * 60)
            context['list_of_targets'] = table
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
                description = retrieving_atc_description(slug).name
                context = dict()
                cache.set("description_by_atc_data_" + slug, description, 60 * 60)
            context['description'] = description
            # print("context : ", context)
        return context


def retrieving_atc_description(level):
    if level.lower()=="anatomical":
        return list(AtcAnatomicalGroup.objects.all().values_list("id", "name"))
    else:
        if level.lower()=="therapeutic":
            return list(AtcTherapeuticGroup.objects.all().values_list("id", "name"))
        else:
            if level.lower()=="pharmacological":
                return list(AtcPharmacologicalGroup.objects.all().values_list("id", "name"))
            else:
                if level.lower()=="chemical":
                    return list(AtcChemicalGroup.objects.all().values_list("id", "name"))
                else:
                    return list(AtcChemicalSubstance.objects.all().values_list("id", "name"))

class AtcCodesByLevelBaseView:
    def get_atc_codes_by_level(self, slug):
        context = {}
        if slug is not None:
            if cache.get("atc_codes_by_level_" + slug) is not None:
                list_of_codes = cache.get("atc_codes_by_level_" + slug)
            else:
                list_of_codes = retrieving_atc_description(slug)
                context = dict()
                cache.set("atc_codes_by_level_" + slug, list_of_codes, 60 * 60)
            context['list_of_codes'] = list_of_codes
            # print("context : ", context)
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
            # print("context : ", context)
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
            # print("context : ", context)
        return context
    

class PGxByAtcCodeView:
    def get_pgx_by_atc_code(self, slug):
        context = {}
        if slug is not None:
            if cache.get("pgx_by_atc_codes_" + slug) is not None:
                returned_data = cache.get("pgx_by_atc_codes_" + slug)
            else:
                pgx = ""
                returned_data = []
                # for code in pgx:
                #     name = AtcChemicalSubstance.objects.get(id=code[0]).name
                #     returned_data.append({"Atc code": code, "Description": name })

                context = dict()
                cache.set("pgx_by_atc_codes_" + slug, returned_data, 60 * 60)
            context['pgx'] = returned_data
            # print("context : ", context)
        return context
    
class DrugTargetInteractionByAtcBaseView:
    def get_interaction_by_atc_code(self, slug):
        context = {}
        if slug is not None:
            if cache.get("interactions_by_atc_code_" + slug) is not None:
                returned_data = cache.get("interactions_by_atc_code_" + slug)
            else:
                drug_ids = DrugAtcAssociation.objects.filter(atc_id=slug).values_list("drug_id", flat=True)
                returned_data = []
                for drug_id in drug_ids:
                    interactions = Interaction.objects.filter(drug_bankID=drug_id).values_list("uniprot_ID", "actions", "known_action", "interaction_type")
                    # print("interactions: ", interactions)
                    for interaction in interactions:
                        # print("--- interaction: ", interaction)
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
            # print("context: ", context)
        return context
    