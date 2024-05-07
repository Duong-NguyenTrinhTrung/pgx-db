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
from variant.models import Variant, VepVariant, GenebassPGx, GenebassVariantPGx, Pharmgkb, VariantMapper
from interaction.models import Interaction
from gene.models import Gene
from disease.models import Disease, DrugDiseaseStudy
from drug.models import Drug, DrugAtcAssociation
from chromosome.models import Chromosome
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist

def variant_mapper(request):
    context = {}
    return render(request, 'home/variant_mapper.html', context)

def get_variant_mapping(request):
    pass

def get_variant_mapping_example(request):
    pass

def variant_anno_from_autocomplete_view(request):
    pass

def anno_from_autocomplete_view(request):
    version = request.GET.get('version')
    anno_from = request.GET.get('anno_from')
    query = request.GET.get('query', "")
    anno_from_examples=[]

    if (anno_from=="ensembl"):
        anno_from_examples = list(Chromosome.objects.filter(Q(genome_version=version)&Q(ensembl__icontains=query)).values_list("ensembl", flat=True))
    if (anno_from=="ucsc"):
        anno_from_examples = list(Chromosome.objects.filter(Q(genome_version=version)&Q(ucsc__icontains=query)).values_list("ucsc", flat=True))
    if (anno_from=="refseq"):
        anno_from_examples = list(Chromosome.objects.filter(Q(genome_version=version)&Q(refseq__icontains=query)).values_list("refseq", flat=True))
    if (anno_from=="gencode"):
        anno_from_examples = list(Chromosome.objects.filter(Q(genome_version=version)&Q(gencode__icontains=query)).values_list("gencode", flat=True))
    if (anno_from=="ncbi"):
        anno_from_examples = list(Chromosome.objects.filter(Q(genome_version=version)&Q(ncbi__icontains=query)).values_list("ncbi", flat=True))

    anno_from_examples = list(set(anno_from_examples))
    anno_from_examples = [d for d in anno_from_examples if not d==""]
    return JsonResponse({'suggestions': anno_from_examples})

def protein_autocomplete_view(request):
    query = request.GET.get('query', '')
    proteins = Protein.objects.filter(Q(uniprot_ID__icontains=query) | Q(protein_name__icontains=query) | Q(geneID__icontains=query) | Q(genename__icontains=query))
    result_uniprot_id = Protein.objects.filter(uniprot_ID__icontains=query)
    
    if len(result_uniprot_id) == 0:
        result_protein_name = Protein.objects.filter(protein_name__icontains=query)
        if len(result_protein_name) == 0:
            result_gene_id = Protein.objects.filter(geneID__icontains=query)
            if len(result_gene_id) == 0:
                result_genename = Protein.objects.filter(genename__icontains=query)
                results = [protein.genename for protein in result_genename]
            else:
                results = [protein.geneID for protein in result_gene_id]
        else:
            results = [protein.protein_name for protein in result_protein_name]
    else:
        results = [protein.uniprot_ID for protein in result_uniprot_id]
    # results = [protein.geneID + "(" + protein.genename + ") " + protein.uniprot_ID + " (" + protein.protein_name +")" for protein in proteins]
    return JsonResponse({'suggestions': results})

def variant_autocomplete_view(request):
    query = request.GET.get('query', '')
    # variants = Variant.objects.filter(Q(VariantMarker__icontains=query))
    variants = Variant.objects.filter(
        Q(VariantMarker__icontains=query) | 
        Q(Gene_ID__gene_id__icontains=query) | 
        Q(Gene_ID__genename__icontains=query)
    )
    # if len(variants) > 0:
    #     results = [variant.VariantMarker + " in gene "+ variant.Gene_ID.genename +" (" + variant.Gene_ID.gene_id +")" for variant in variants]
    # return JsonResponse({'suggestions': results})
    results = []
    if variants.exists():
        results = [
            variant.VariantMarker + " in gene " + variant.Gene_ID.genename +
            " (" + variant.Gene_ID.gene_id + ")"
            for variant in variants
        ]
    return JsonResponse({'suggestions': results})

def drug_autocomplete_view(request):
    query = request.GET.get('query', '')
    drugs = Drug.objects.filter(Q(drug_bankID__icontains=query)|Q(name__icontains=query))
    if len(drugs) > 0:
        results = [drug.drug_bankID + " - "+ drug.name for drug in drugs]
    return JsonResponse({'suggestions': results})

class Home(TemplateView):
    template_name = 'index_pharmcodb.html'
    # no_of_drugs = len(Drug.objects.all())
    # no_of_proteins = len(Protein.objects.all())
    # no_of_interactions = len(Interaction.objects.all())
    # no_of_vm = len(Variant.objects.all())
    # no_of_vep_variant = len(VepVariant.objects.all())
    # no_of_genebase_pgx = len(GenebassPGx.objects.all())
    # no_of_variant_based_pgx = len(GenebassVariantPGx.objects.all())
    # no_of_pharmgkb = len(Pharmgkb.objects.all())
    context = {
                # "no_of_drugs": no_of_drugs,
                # "no_of_proteins": no_of_proteins,
                # "no_of_interactions": no_of_interactions,
                # "no_of_vm": no_of_vm,
                # "no_of_vep_variant": no_of_vep_variant,
                # "no_of_genebase_pgx": no_of_genebase_pgx,
                # "no_of_variant_based_pgx": no_of_variant_based_pgx,
                # "no_of_pharmgkb": no_of_pharmgkb,
               }

def common_menu(request):
    context = {
        'DOCUMENTATION_URL': settings.DOCUMENTATION_URL,  # Add DOCUMENTATION_URL to the context
    }
    return render(request, 'home/common_menu.html', context)

# http://localhost:8000/get_chromosome_mapping/?version=GRCh38&anno1=ensembl&input=22&anno2=ucsc
def get_chromosome_mapping(request):
    version = request.GET.get("version")
    anno_from = request.GET.get("anno_from")
    anno_to = request.GET.get("anno_to")
    input = request.GET.get("input")
    # ensembl, gencode, genome_version, id, ncbi, refseq, ucsc
    if (anno_from=="ensembl"):
        data = list(Chromosome.objects.filter(Q(genome_version=version)&Q(ensembl=input)).values_list(anno_to, flat=True))
    if (anno_from=="gencode"):
        data = list(Chromosome.objects.filter(Q(genome_version=version)&Q(gencode=input)).values_list(anno_to, flat=True))
    if (anno_from=="ncbi"):
        data = list(Chromosome.objects.filter(Q(genome_version=version)&Q(ncbi=input)).values_list(anno_to, flat=True))
    if (anno_from=="refseq"):
        data = list(Chromosome.objects.filter(Q(genome_version=version)&Q(refseq=input)).values_list(anno_to, flat=True))
    if (anno_from=="ucsc"):
        data = list(Chromosome.objects.filter(Q(genome_version=version)&Q(ucsc=input)).values_list(anno_to, flat=True))
    data = list(set(data))
    data = [d for d in data if not d==""]
    if len(data)==0:
        data="None"
    context = {
        "result": data
    }
    print("---get_chromosome_mapping ->context ", context)
    return JsonResponse(context)


def get_chromosome_mapping_example(request):
    version = request.GET.get("version")
    anno_from = request.GET.get("anno_from")
    anno_to = request.GET.get("anno_to")
    anno_from_example=[]
    anno_to_example=[]

    print("paras: ",version, " ", anno_from, " ", anno_to)

    if (anno_from=="ensembl"):
        anno_from_example = list(Chromosome.objects.filter(genome_version=version).values_list("ensembl", flat=True))
    if (anno_from=="gencode"):
        anno_from_example = list(Chromosome.objects.filter(genome_version=version).values_list("gencode", flat=True))
    if (anno_from=="ncbi"):
        anno_from_example = list(Chromosome.objects.filter(genome_version=version).values_list("ncbi", flat=True))
    if (anno_from=="refseq"):
        anno_from_example = list(Chromosome.objects.filter(genome_version=version).values_list("refseq", flat=True))
    if (anno_from=="ucsc"):
        anno_from_example = list(Chromosome.objects.filter(genome_version=version).values_list("ucsc", flat=True))
    anno_from_example = list(set(anno_from_example))
    anno_from_example = [d for d in anno_from_example if not d==""]

    if (anno_to=="ensembl"):
        anno_to_example = list(Chromosome.objects.filter(genome_version=version).values_list("ensembl", flat=True))
    if (anno_to=="gencode"):
        anno_to_example = list(Chromosome.objects.filter(genome_version=version).values_list("gencode", flat=True))
    if (anno_to=="ncbi"):
        anno_to_example = list(Chromosome.objects.filter(genome_version=version).values_list("ncbi", flat=True))
    if (anno_to=="refseq"):
        anno_to_example = list(Chromosome.objects.filter(genome_version=version).values_list("refseq", flat=True))
    if (anno_to=="ucsc"):
        anno_to_example = list(Chromosome.objects.filter(genome_version=version).values_list("ucsc", flat=True))
    anno_to_example = list(set(anno_to_example))
    anno_to_example = [d for d in anno_to_example if not d==""]

    if len(anno_from_example)>0:
        anno_from_example=anno_from_example[0]
    else:
        anno_from_example="None"

    if len(anno_to_example)>0:
        anno_to_example=anno_to_example[0]
    else:
        anno_to_example="None"

    context = {
        "anno_from_example": anno_from_example,
        "anno_to_example": anno_to_example
    }
    print("context = ", context)
    return JsonResponse(context)

def chromosome_mapper(request):
    context = {}
    return render(request, 'home/chromosome_mapper.html', context)

def drug_target_network(request):
    context = {}
    return render(request, 'home/drug_and_target_network.html', context)
    # return render(request, 'home/drug_and_target_network copy.html', context)

def tutorial(request):
    context = {}
    return render(request, 'home/tutorial.html', context)


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
            data = Drug.objects.all()[:30]
        drugs = []
        for item in data:
            atc_code = DrugAtcAssociation.objects.filter(drug_id=item.drug_bankID).values_list('atc_id', flat=True)
            if len(atc_code)==0:
                code = "Not assigned"
            else:
                code = list(atc_code)
            drugs.append({
                'drug_bankID': item.drug_bankID,
                'name': item.name,
                'atc_code': code,
                'drug_type': item.drugtype.type_detail,
                'Clinical_status': clinical_status_dict.get(item.Clinical_status)
            })
        print("drugs : ", drugs)
        return JsonResponse({'drugs': drugs})
    else:
        data = Drug.objects.all()[:30]
        drugs = []
        for item in data:
            atc_code = DrugAtcAssociation.objects.filter(drug_id=item.drug_bankID).values_list('atc_id', flat=True)
            if len(atc_code)==0:
                code = "Not assigned"
            else:
                code = list(atc_code)

            drugs.append({
                'drug_bankID': item.drug_bankID,
                'name': item.name,
                'atc_code': code,
                'drug_type': item.drugtype.type_detail,
                'Clinical_status': clinical_status_dict.get(item.Clinical_status)
            })
        context["drugs"] = drugs
        print("context ", context)
        return render(request, 'home/drug_lookup.html', context)
    
def get_atc_code(drug_bankID):
    try:
        drug_atc_association = DrugAtcAssociation.objects.filter(drug_id=drug_bankID).first()
        return drug_atc_association.atc_id.id if drug_atc_association else None
    except ObjectDoesNotExist:
        return None

def variant_lookup(request):
    context = {}
    variant_id = request.GET.get('variant_id')
    if variant_id:
        if variant_id != 'default':
            objects = Variant.objects.filter(VariantMarker__icontains=variant_id)
        else:
            objects = Variant.objects.all()[:30]
        variants = []
        for item in objects:
            variants.append({
                "VariantMarker": item.VariantMarker,
                'genename': item.Gene_ID.genename,
                'geneID': item.Gene_ID.gene_id,
                'pt': item.Gene_ID.primary_transcript, # primary transcript
            })
        return JsonResponse({'variants': variants})
    else:
        objects = Variant.objects.all()[:30]
        variants = []
        for item in objects:
            variants.append({
                "VariantMarker": item.VariantMarker,
                'genename': item.Gene_ID.genename,
                'geneID': item.Gene_ID.gene_id,
                'pt': item.Gene_ID.primary_transcript, # primary transcript
            })
        return render(request, 'home/variant_lookup.html', {'variants': variants})
        # return render(request, 'home/Drugs_Indications_Targets.html', {'variants': variants})

def target_lookup(request):
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
            print("target is default, get 6 records")
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
        # If no target parameter provided, get 6 records
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
    enzyme_cate = ["substrate", "inhibitor", "substrate|inhibitor", "inducer", "substrate|inducer", "substrate|inhibitor|inducer", "inhibitor|inducer", "ligand", "cofactor", "other"]
    target_cate = ["inhibitor", "antagonist", "agonist", "binder", "ligand", "cofactor", "activator", "potentiator", "inducer", "substrate", "partial agonist", "other"]
    transporter_cate = ["inhibitor", "substrate", "substrate|inhibitor", "inducer", "substrate|inhibitor|inducer", "inhibitor|inducer", "substrate|inducer", "transporter", "other"] 
    carrier_cate = ["binder", "substrate", "substrate|inhibitor", "inducer", "inhibitor", "ligand", "antagonist", "agonist", "carrier", "other"] 
    

    context = {
        "no_of_target": Interaction.objects.filter(interaction_type="target").count(),
        "no_of_enzyme": Interaction.objects.filter(interaction_type="enzyme").count(),
        "no_of_transporter": Interaction.objects.filter(interaction_type="transporter").count(),
        "no_of_carrier": Interaction.objects.filter(interaction_type="carrier").count(),
        "total": Interaction.objects.filter(interaction_type="target").count()+ Interaction.objects.filter(interaction_type="enzyme").count()+Interaction.objects.filter(interaction_type="transporter").count()+Interaction.objects.filter(interaction_type="carrier").count(),
        "enzyme_cate": enzyme_cate, 
        "target_cate": target_cate, 
        "transporter_cate": transporter_cate, 
        "carrier_cate": carrier_cate, 

        #protein class = ion channel
        "ion_class":
        {
            "enzyme":
            [
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & ~Q(actions__in=enzyme_cate[:-1]) & Q(uniprot_ID__Protein_class="Ion channel")).count(),
            ],

            "target":
                [
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="activator") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="potentiator") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="partial agonist") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & ~Q(actions__in=target_cate[:-1]) & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                ],

            "transporter":
            [
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="transporter") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & ~Q(actions__in=transporter_cate[:-1]) & Q(uniprot_ID__Protein_class="Ion channel")).count(),
            ],

            "carrier":
            [
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="carrier") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Ion channel")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & ~Q(actions__in=carrier_cate[:-1]) & Q(uniprot_ID__Protein_class="Ion channel")).count(),
            ]
        },
        #protein class = Enzyme
        "enzyme_class":
        {
            "enzyme":
            [
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & ~Q(actions__in=enzyme_cate[:-1]) & Q(uniprot_ID__Protein_class="Enzyme")).count(),
            ],

            "target":
            [
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="activator") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="potentiator") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="partial agonist") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & ~Q(actions__in=target_cate[:-1]) & Q(uniprot_ID__Protein_class="Enzyme")).count(),
            ],

            "transporter":
            [
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="transporter") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & ~Q(actions__in=transporter_cate[:-1]) & Q(uniprot_ID__Protein_class="Enzyme")).count(),
            ],

            "carrier":
            [
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="carrier") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Enzyme")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & ~Q(actions__in=carrier_cate[:-1]) & Q(uniprot_ID__Protein_class="Enzyme")).count(),
            ]
        },

        #protein class = Epigenetic regulator
        "epi_class":
        {
            "enzyme":
            [
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & ~Q(actions__in=enzyme_cate[:-1]) & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
            ],

            "target":
            [
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="activator") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="potentiator") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="partial agonist") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & ~Q(actions__in=target_cate[:-1]) & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
            ],

            "transporter":
            [
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="transporter") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & ~Q(actions__in=transporter_cate[:-1]) & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
            ],

            "carrier":
            [
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="carrier") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & ~Q(actions__in=carrier_cate[:-1]) & Q(uniprot_ID__Protein_class="Epigenetic regulator")).count(),
            ]       
        },

        #protein class = Kinase
        "kinase_class":
        {
            "enzyme":
            [
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & ~Q(actions__in=enzyme_cate[:-1]) & Q(uniprot_ID__Protein_class="Kinase")).count(),
            ],

            "target":
            [
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="activator") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="potentiator") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="partial agonist") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & ~Q(actions__in=target_cate[:-1]) & Q(uniprot_ID__Protein_class="Kinase")).count(),
            ],

            "transporter":
            [
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="transporter") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & ~Q(actions__in=transporter_cate[:-1]) & Q(uniprot_ID__Protein_class="Kinase")).count(),
            ],

            "carrier":
            [
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="carrier") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Kinase")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & ~Q(actions__in=carrier_cate[:-1]) & Q(uniprot_ID__Protein_class="Kinase")).count(),
            ]   
        },

        #protein class = Nuclear receptor
        "nu_class":
        {
            "enzyme":
            [
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & ~Q(actions__in=enzyme_cate[:-1]) & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
            ],

            "target":
            [
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="activator") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="potentiator") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="partial agonist") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & ~Q(actions__in=target_cate[:-1]) & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
            ],

            "transporter":
            [
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="transporter") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & ~Q(actions__in=transporter_cate[:-1]) & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
            ],

            "carrier":
            [
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="carrier") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & ~Q(actions__in=carrier_cate[:-1]) & Q(uniprot_ID__Protein_class="Nuclear receptor")).count(),
            ]
        },

        #protein class = GPCR
        "gpcr_class":
        {
            "enzyme":
            [
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & ~Q(actions__in=enzyme_cate[:-1]) & Q(uniprot_ID__Protein_class="GPCR")).count(),
            ],

            "target":
            [
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="binder") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="activator") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="potentiator") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="partial agonist") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & ~Q(actions__in=target_cate[:-1]) & Q(uniprot_ID__Protein_class="GPCR")).count(),
            ],
            "transporter":
            [
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="transporter") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & ~Q(actions__in=transporter_cate[:-1]) & Q(uniprot_ID__Protein_class="GPCR")).count(),
            ],
            "carrier":
            [
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="binder") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="carrier") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="GPCR")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & ~Q(actions__in=carrier_cate[:-1]) & Q(uniprot_ID__Protein_class="GPCR")).count(),
            ],
        },

        #protein class = Transporter
        "trans_class":
        {
            "enzyme":
            [
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & ~Q(actions__in=enzyme_cate[:-1]) & Q(uniprot_ID__Protein_class="Transporter")).count(),
            ],
            "target":
            [
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="activator") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="potentiator") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="partial agonist") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & ~Q(actions__in=target_cate[:-1]) & Q(uniprot_ID__Protein_class="Transporter")).count(),
            ],
            "transporter":
            [
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="transporter") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & ~Q(actions__in=transporter_cate[:-1]) & Q(uniprot_ID__Protein_class="Transporter")).count(),
            ],
            "carrier":
            [
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="carrier") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Transporter")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & ~Q(actions__in=carrier_cate[:-1]) & Q(uniprot_ID__Protein_class="Transporter")).count(),
            ]
        },

        #protein class = Unknown
        "unknown_class":
        {
            "enzyme":
            [
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="enzyme") & ~Q(actions__in=enzyme_cate[:-1]) & Q(uniprot_ID__Protein_class="Unknown")).count(),
            ],
            "target":
            [
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="cofactor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="activator") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="potentiator") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & Q(actions="partial agonist") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="target") & ~Q(actions__in=target_cate[:-1]) & Q(uniprot_ID__Protein_class="Unknown")).count(),
            ],
            "transporter":
            [
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inhibitor|inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="inhibitor|inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="substrate|inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & Q(actions="transporter") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="transporter") & ~Q(actions__in=transporter_cate[:-1]) & Q(uniprot_ID__Protein_class="Unknown")).count(),
            ],
            "carrier":
            [
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="binder") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="carrier") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inducer") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="inhibitor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="ligand") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="antagonist") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="agonist") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & Q(actions="substrate|inhibitor") & Q(uniprot_ID__Protein_class="Unknown")).count(),
                Interaction.objects.filter(Q(interaction_type="carrier") & ~Q(actions__in=carrier_cate[:-1]) & Q(uniprot_ID__Protein_class="Unknown")).count(),
            ]
        }
    }

    # print("context = ", context)
    return render(request,  'home/target_statistics.html', context)

def about_pgx(request):
    context = {}
    return render(request, 'home/about_pgx.html', context)

def questions_to_pgx(request):
    context = {}
    return render(request, 'home/questions_to_pgx.html', context)

def contribute_to_pgx(request):
    context = {}
    return render(request, 'home/contribute_to_pgx.html', context)

def disease_lookup(request):
    disease = request.GET.get('disease')
    print("disease requested = ", disease)
    context = {}
    if disease:
        if disease != 'default':
            print("are we here at disease != default???")
            diseases = Disease.objects.filter(disease_name__icontains=disease)
        else:
            print("are we here at disease = default???")
            diseases = Disease.objects.all()[:8]
        response_data = []
        for d in diseases:
                temp=[]
                drugs = DrugDiseaseStudy.objects.filter(disease_name__disease_name=d.disease_name).values_list('drug_bankID', 'clinical_trial', 'link')
                for item in drugs:
                    temp.append({
                        'drug_bankID': item[0],
                        'drugname': Drug.objects.get(drug_bankID=item[0]).name,
                        'clinical_trial': item[1],
                        'link': item[2],
                        'atc_code': str(DrugAtcAssociation.objects.filter(drug_id=item[0]).values_list('atc_id', flat=True).first()),
                        })
                response_data.append({
                    'disease_name':d.disease_name,
                    'disease_class': d.disease_class,
                    'disease_UML_CUI': d.disease_UML_CUI,
                    "drugs": temp,
                })
            
        print("there is disease para, length = ",len(response_data))
        print("response_data = ", response_data)
        # context["response_data"] = response_data
        return JsonResponse({'response_data': response_data})
        # return render(request, 'home/disease_lookup.html', context)
    else:
        diseases = Disease.objects.all()[:8]
        response_data = []
        for d in diseases:
                temp=[]
                drugs = DrugDiseaseStudy.objects.filter(disease_name__disease_name=d.disease_name).values_list('drug_bankID', 'clinical_trial', 'link')
                for item in drugs:
                    temp.append({
                        'drug_bankID': item[0],
                        'drugname': Drug.objects.get(drug_bankID=item[0]).name,
                        'clinical_trial': item[1],
                        'link': item[2],
                        'atc_code': str(DrugAtcAssociation.objects.filter(drug_id=item[0]).values_list('atc_id', flat=True).first()),
                        })
                response_data.append({
                    'disease_name':d.disease_name,
                    'disease_class': d.disease_class,
                    'disease_UML_CUI': d.disease_UML_CUI,
                    "drugs": temp,
                })
        context["response_data"] = response_data
        print("there is no disease para, length = ",len(response_data))
        print("response data: ", response_data)
        return render(request, 'home/disease_lookup.html', context)

def disease_statistics(request):
    no_of_phase1 = len(list(set(DrugDiseaseStudy.objects.filter(clinical_trial="1").values_list("drug_bankID", "disease_name"))))
    no_of_phase2 = len(list(set(DrugDiseaseStudy.objects.filter(clinical_trial="2").values_list("drug_bankID", "disease_name"))))
    no_of_phase3 = len(list(set(DrugDiseaseStudy.objects.filter(clinical_trial="3").values_list("drug_bankID", "disease_name"))))
    no_of_phase4 = len(list(set(DrugDiseaseStudy.objects.filter(clinical_trial="4").values_list("drug_bankID", "disease_name"))))
    disease_classes = list(Disease.objects.values_list('disease_class', flat=True).distinct())

    
    context = {
        "no_of_phase1": no_of_phase1,
        "no_of_phase2": no_of_phase2,
        "no_of_phase3": no_of_phase3,
        "no_of_phase4": no_of_phase4,
        "total": no_of_phase1 + no_of_phase2 + no_of_phase3 + no_of_phase4,
        "disease_classes": disease_classes,

        "biologic":
        {
            "phase1": [DrugDiseaseStudy.objects.filter(Q(clinical_trial="1")&Q(drug_bankID__drugtype__type_detail="Biotech") & Q(disease_name__disease_class=dc)).count() for dc in disease_classes],
            "phase2": [DrugDiseaseStudy.objects.filter(Q(clinical_trial="2")&Q(drug_bankID__drugtype__type_detail="Biotech") & Q(disease_name__disease_class=dc)).count() for dc in disease_classes],
            "phase3": [DrugDiseaseStudy.objects.filter(Q(clinical_trial="3")&Q(drug_bankID__drugtype__type_detail="Biotech") & Q(disease_name__disease_class=dc)).count() for dc in disease_classes],
            "phase4": [DrugDiseaseStudy.objects.filter(Q(clinical_trial="4")&Q(drug_bankID__drugtype__type_detail="Biotech") & Q(disease_name__disease_class=dc)).count() for dc in disease_classes],
        },
        "small_molecule":
        {
            "phase1": [DrugDiseaseStudy.objects.filter(Q(clinical_trial="1")&Q(drug_bankID__drugtype__type_detail="Small Molecule") & Q(disease_name__disease_class=dc)).count() for dc in disease_classes],
            "phase2": [DrugDiseaseStudy.objects.filter(Q(clinical_trial="2")&Q(drug_bankID__drugtype__type_detail="Small Molecule") & Q(disease_name__disease_class=dc)).count() for dc in disease_classes],
            "phase3": [DrugDiseaseStudy.objects.filter(Q(clinical_trial="3")&Q(drug_bankID__drugtype__type_detail="Small Molecule") & Q(disease_name__disease_class=dc)).count() for dc in disease_classes],
            "phase4": [DrugDiseaseStudy.objects.filter(Q(clinical_trial="4")&Q(drug_bankID__drugtype__type_detail="Small Molecule") & Q(disease_name__disease_class=dc)).count() for dc in disease_classes],
        },
    }

    print("context ======== ", context)

    return render(request, 'home/disease_statistics.html', context)


def disease_autocomplete_view(request):
    query = request.GET.get('query', '')
    diseases = Disease.objects.filter(Q(disease_name__icontains=query))
    if len(diseases) > 0:
        results = [disease.disease_name  for disease in diseases]
    else:
        results = []
    print("inside disease_autocomplete_view : ", results)
    return JsonResponse({'suggestions': results})
