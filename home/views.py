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
from drug.models import Drug, DrugAtcAssociation, AdverseDrugReaction, SideEffect
from chromosome.models import Chromosome
from django.conf import settings
from django.http import JsonResponse
from django.db.models import Q
from django.core.exceptions import ObjectDoesNotExist
from urllib.parse import unquote

def adr_lookup(request):
    se_name = request.GET.get('se_name')
    adr = []
    if se_name: # if the request is sent with para
        if se_name!="default": # if the request para is not "default", i.e., http://localhost:8000/adr_lookup/?se_name=Influenza
            print("a query term is passed for adr_lookup")
            data = SideEffect.objects.filter(side_effect_name=se_name)[:1]
        else: # if the request para is "default"
            print("default para is passed for adr_lookup")
            data = SideEffect.objects.all()[:2] # return None if there is no instance

        if data:
            for item in data:
                reactions = AdverseDrugReaction.objects.filter(adr_data__icontains=item.side_effect_name)
                drug_and_freqs = []
                for reaction in reactions:
                    drug_bankID = reaction.drug_bankID.drug_bankID
                    drug_name = reaction.drug_bankID.name
                    try:
                        atc_code = DrugAtcAssociation.objects.get(drug_id=drug_bankID).atc_id.id
                    except:
                        atc_code = "Not assigned"
                    se_pairs = reaction.adr_data.split(",")
                    fre = 0
                    color = ""
                    for p in se_pairs:
                        if p.find(item.side_effect_name.lower())>0:
                            fre = float(p.split()[-1][1:-2])
                            if fre<=25:
                                color = "color1"
                            elif fre<=50:
                                color = "color2"
                            elif fre<=75:
                                color = "color3"
                            else:
                                color = "color4"
                            break
                    drug_and_freqs.append({"drugbank_id": drug_bankID,
                                            "drug_name": drug_name,
                                            "atc_code": atc_code,
                                            "frequency": fre, "color": color})
                    drug_and_freqs = sorted(drug_and_freqs, key=lambda x: x["frequency"], reverse=True)
                adr.append({"se_name": item.side_effect_name, "se_definition": item.side_effect_definition, "drug_and_freq": drug_and_freqs})
    else: # if the request is sent without para
        print("no para is passed for adr_lookup")
        data = SideEffect.objects.all()[:2]
        # se_definition = list(se_instance.values_list("side_effect_definition", flat=True))
        print("data  ", data)
        for item in data:
            reactions = AdverseDrugReaction.objects.filter(adr_data__icontains=item.side_effect_name)
            drug_and_freqs = []
            for reaction in reactions:
                drug_bankID = reaction.drug_bankID.drug_bankID
                drug_name = reaction.drug_bankID.name
                try:
                    atc_code = DrugAtcAssociation.objects.get(drug_id=drug_bankID).atc_id.id
                except:
                    atc_code = "Not assigned"
                se_pairs = reaction.adr_data.split(",")
                print("item.side_effect_name ", item.side_effect_name)
                print("se_pairs :", se_pairs)
                fre = "None"#
                color = "black"
                for pair in se_pairs:
                    pair = pair.trim()
                    adr_term = " ".join(pair.split()[:-1])
                    if adr_term.find(item.side_effect_name.lower())>0:
                        fre = float(p.split()[-1][1:-2])
                        if fre<=25:
                            color = "color1"
                        elif fre<=50:
                            color = "color2"
                        elif fre<=75:
                            color = "color3"
                        else:
                            color = "color4"
                        break
                print("fre ", fre, " color ", color)
                drug_and_freqs.append({"drugbank_id": drug_bankID,
                                        "drug_name": drug_name,
                                        "atc_code": atc_code,
                                        "frequency": fre, "color": color})
                drug_and_freqs = sorted(drug_and_freqs, key=lambda x: x["frequency"], reverse=True)
            adr.append({"se_name": item.side_effect_name, "se_definition": item.side_effect_definition, "drug_and_freq": drug_and_freqs})
    context = {}
    context["data"] = adr
    # print("se " , context)
    return render(request, 'home/adr_lookup.html', context)
    

def adr_autocomplete_view(request):
    pass

def get_atc_code_statistics(request):
    context = {}
    return render(request, 'home/atc_code_statistics.html', context)

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
    query = request.GET.get('query', '').split(";")[-1]
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
    return JsonResponse({'suggestions': results})

def variant_autocomplete_view(request):
    query = request.GET.get('query', '').split(";")[-1]
    variants = Variant.objects.filter(
        Q(VariantMarker__icontains=query) | 
        Q(Gene_ID__gene_id__icontains=query) | 
        Q(Gene_ID__genename__iexact=query)
    )
    results = []
    if variants.exists():
        number_variants = len(variants)
        if len(variants) > 20:
            variants = variants[:20]
        results = [
            variant.VariantMarker + " in gene " + variant.Gene_ID.genename +
            " (" + variant.Gene_ID.gene_id + ")"
            for variant in variants
        ]
        if number_variants > 20:
            results.append(f"20/{number_variants} results are showed")
    return JsonResponse({'suggestions': results})

def drug_autocomplete_view(request):
    query = request.GET.get('query', '').split(";")[-1]
    drugs = Drug.objects.filter(Q(drug_bankID__icontains=query)|Q(name__icontains=query))
    results = []
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
    return JsonResponse(context)


def get_chromosome_mapping_example(request):
    version = request.GET.get("version")
    anno_from = request.GET.get("anno_from")
    anno_to = request.GET.get("anno_to")
    anno_from_example=[]
    anno_to_example=[]

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

def use_case_examples(request):
    context = {}
    return render(request, 'home/use_case_examples.html', context)

def sort_dict(my_dict):
    sorted_items_desc = sorted(my_dict.items(), key=lambda item: item[1], reverse = True)
    sorted_dict_desc = dict(sorted_items_desc)
    return sorted_dict_desc

def get_se_definition(request):
    se_name = request.GET.get("se-name")
    try:
        definition = SideEffect.objects.get(side_effect_name=se_name).side_effect_definition
    except SideEffect.DoesNotExist:
        definition = "NA"

    context = {
        "se_definition": definition
    }
    return JsonResponse(context)

def get_adr(drugbank_id):
    try:
        adr_instance = AdverseDrugReaction.objects.filter(drug_bankID=drugbank_id).first()
        # Check if an instance was found
        if adr_instance:
            adr_data = adr_instance.adr_data
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
                    "color4": sort_dict(color4_data), 
                    "color3": sort_dict(color3_data), 
                    "color2": sort_dict(color2_data), 
                    "color1": sort_dict(color1_data), 
                }
            no_of_se = len(pairs)
            print("drugbank_id ", drugbank_id, " no_of_se ", no_of_se)
        else:
            adr = "NA"  
            no_of_se = 0  
        
    except AdverseDrugReaction.DoesNotExist:
        adr = "NA"

    return adr, no_of_se

def drug_lookup(request):
    input = request.GET.get('drug')
    print("inside drug_lookup view : ", input)
    clinical_status_dict = {0: "Nutraceutical", 1: "Experimental", 2: "Investigational", 3: "Approved", 4: "Vet approved", 5: "Illicit"}
    context = {}
    results = []
    if input:
        if input != 'default':
            try:
                if input.find(" - ")>0:
                    drug_ids = [drug.split(" - ")[0] for drug in input.split(";")]
                    drug_names = [drug.split(" - ")[1] for drug in input.split(";")]
                    # print("-- drug_ids ", drug_ids)
                    # print("-- drug_names ", drug_names)
                    if len(drug_ids)>1:
                        data = Drug.objects.filter(
                            Q(drug_bankID__in=drug_ids) |
                            Q(name__in=drug_names))
                    else:
                        data = Drug.objects.filter(
                            Q(drug_bankID=drug_ids[0]) |
                            Q(name=drug_names[0]))
                else:
                    drug_ids = input.split(";")
                    data = Drug.objects.filter(
                            drug_bankID__in=drug_ids
                            )
            except Exception as e:
                print("Exception ", e)
                data = []
        else:
            data = Drug.objects.all()[:20]
        
        for item in data:
            atc_code = DrugAtcAssociation.objects.filter(drug_id=item.drug_bankID).values_list('atc_id', flat=True)
            if len(atc_code)==0:
                code = "Not assigned"
            else:
                code = list(atc_code)
            adr, no_of_se = get_adr(item.drug_bankID)
            if adr!="NA":
                adr_json = {
                    "color4": [f"{key} ({value}" for key, value in adr.get("color4", {}).items()],
                    "color3": [f"{key} ({value}" for key, value in adr.get("color3", {}).items()],
                    "color2": [f"{key} ({value}" for key, value in adr.get("color2", {}).items()],
                    "color1": [f"{key} ({value}" for key, value in adr.get("color1", {}).items()],
                }
            else:
                adr_json = "NA"
            results.append({
                'drug_bankID': item.drug_bankID,
                'name': item.name,
                'atc_code': code,
                'drug_type': item.drugtype.type_detail,
                'Clinical_status': clinical_status_dict.get(item.Clinical_status),
                "adr": adr,
                "adr_json": adr_json,
                "no_of_size_effects": no_of_se,
            })
        return JsonResponse({'drugs': results})
    else:
        data = Drug.objects.all()[:20]
        for item in data:
            atc_code = DrugAtcAssociation.objects.filter(drug_id=item.drug_bankID).values_list('atc_id', flat=True)
            if len(atc_code)==0:
                code = "Not assigned"
            else:
                code = list(atc_code)
            adr, no_of_se = get_adr(item.drug_bankID)
            if adr!="NA":
                adr_json = {
                    "color1": [f"{key} ({value}" for key, value in adr.get("color1", {}).items()],
                    "color2": [f"{key} ({value}" for key, value in adr.get("color2", {}).items()],
                    "color3": [f"{key} ({value}" for key, value in adr.get("color3", {}).items()],
                    "color4": [f"{key} ({value}" for key, value in adr.get("color4", {}).items()],
                }
            else:
                adr_json = "NA"
            results.append({
                'drug_bankID': item.drug_bankID,
                'name': item.name,
                'atc_code': code,
                'drug_type': item.drugtype.type_detail,
                'Clinical_status': clinical_status_dict.get(item.Clinical_status),
                "adr": adr,
                "adr_json": adr_json,
                "no_of_size_effects": no_of_se,
            })
        context["drugs"] = results
        return render(request, 'home/drug_lookup.html', context)
    
    
def get_atc_code(drug_bankID):
    try:
        drug_atc_association = DrugAtcAssociation.objects.filter(drug_id=drug_bankID).first()
        return drug_atc_association.atc_id.id if drug_atc_association else None
    except ObjectDoesNotExist:
        return None

def variant_lookup(request):
    context = {}
    input = request.GET.get('variant_id')
    variants = []
    if input:
        if input != 'default':
            try:
                variant_ids = [q.split(" ")[0].strip() for q in input.split(";")]
                objects = Variant.objects.filter(VariantMarker__in=variant_ids)
            except Exception as e:
                objects = []
        else:
            objects = Variant.objects.all()[:20]
        for item in objects:
            variants.append({
                "VariantMarker": item.VariantMarker,
                'genename': item.Gene_ID.genename,
                'geneID': item.Gene_ID.gene_id,
                'pt': item.Gene_ID.primary_transcript, # primary transcript
            })
        return JsonResponse({'variants': variants})
    else:
        objects = Variant.objects.all()[:20]
        for item in objects:
            variants.append({
                "VariantMarker": item.VariantMarker,
                'genename': item.Gene_ID.genename,
                'geneID': item.Gene_ID.gene_id,
                'pt': item.Gene_ID.primary_transcript, # primary transcript
            })
        return render(request, 'home/variant_lookup.html', {'variants': variants})
        # return render(request, 'home/Drugs_Indications_Targets.html', {'variants': variants})

def variant_search(request):
    context = {}
    variant_id = request.GET.get('variant_id')
    if variant_id:
        if variant_id != 'default':
            objects = Variant.objects.filter(VariantMarker=variant_id)
        else:
            objects = Variant.objects.all()[:20]
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
        objects = Variant.objects.all()[:20]
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
    context = {}
    input = request.GET.get('target')
    print("input: ", input) # Transitional endoplasmic reticulum ATPase (TER ATPase) (EC 3.6.4.6) (15S Mg(2+)-ATPase p97 subunit) (Valosin-containing protein) (VCP)
    items = []
    if input:
        if input != 'default':
            try:
                encoded_targets = [unquote(t) for t in input.split(";")]
                proteins = Protein.objects.filter(
                    Q(uniprot_ID__in = encoded_targets) |
                    Q(protein_name__in = encoded_targets) |
                    Q(geneID__in = encoded_targets) |
                    Q(genename__in = encoded_targets)
                )
            except:
                proteins = []
        else:
            proteins = Protein.objects.all()[:10]
        
        for item in proteins:
            interactions = Interaction.objects.filter(uniprot_ID=item.uniprot_ID)
            items.append({
                'uniprot_ID': item.uniprot_ID,
                'genename': item.genename,
                'geneID': item.geneID,
                'protein_name': item.protein_name,
                'protein_class': Protein.objects.get(uniprot_ID=item.uniprot_ID).Protein_class,
                "drug_data": [
                    {
                        "drug_id": interaction.drug_bankID.drug_bankID,
                        "drug_name": interaction.drug_bankID.name.title(),
                        "atc_code": get_atc_code(interaction.drug_bankID)
                    }
                    for interaction in interactions
                ],
            })
        return JsonResponse({'items': items})
    else:
        proteins = Protein.objects.all()[:10]
        for item in proteins:
            interactions = Interaction.objects.filter(uniprot_ID=item.uniprot_ID)
            items.append({
                'uniprot_ID': item.uniprot_ID,
                'genename': item.genename,
                'geneID': item.geneID,
                'protein_name': item.protein_name,
                'protein_class': Protein.objects.get(uniprot_ID=item.uniprot_ID).Protein_class,
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
    input = request.GET.get('disease')
    # print("-----disease_lookup disease ", input)
    context = {}
    if input:
        
        if input != 'default':
            results = []
            terms = input.split(";")
            for term in terms:
                # from autocomplete selection, we only have disease name
                diseases = Disease.objects.filter(Q(disease_name=term))
                if len(diseases) > 0:
                    for disease in diseases:
                        results.append(disease)
        else: # this is for reset 
            results = Disease.objects.all()[:6]
        response_data = []
        for d in results:
                # print(d, " type ", type(d) )
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
                temp.sort(key=lambda x: int(x['clinical_trial']), reverse=True)
                print("----- temp ", temp)
                response_data.append({
                    'disease_name':d.disease_name,
                    'disease_class': d.disease_class,
                    'disease_UML_CUI': d.disease_UML_CUI,
                    "drugs": temp,
                })
        return JsonResponse({'response_data': response_data})
    else:
        diseases = Disease.objects.all()[:6]
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
                temp.sort(key=lambda x: int(x['clinical_trial']), reverse=True)
                print("----- temp ", temp)
                response_data.append({
                    'disease_name':d.disease_name,
                    'disease_class': d.disease_class,
                    'disease_UML_CUI': d.disease_UML_CUI,
                    "drugs": temp,
                })
        context["response_data"] = response_data
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
    return render(request, 'home/disease_statistics.html', context)

def disease_autocomplete_view(request):
    query = request.GET.get('query', '')
    input = query.split(";")[-1]
    print("input ", input)
    results = []
    # First: assume input is disease name
    diseases = Disease.objects.filter(Q(disease_name__icontains=input)|Q(disease_class__icontains=input))
    if len(diseases) > 0:
        for disease in diseases:
            results.append(disease.disease_name)
    # print("disease related search , result = ", diseases)

    # Second: assume input is drug name
    diseases = DrugDiseaseStudy.objects.filter(drug_bankID__name__icontains=input)
    # print("drug related search , result = ", diseases)
    if len(diseases) > 0:
        for disease in diseases:
            results.append(disease.disease_name.disease_name)

    # Third: assume input is ATC code
    drugs = DrugAtcAssociation.objects.filter(atc_id__id__istartswith=input).values_list('drug_id', flat=True)

    for drug in drugs:
        diseases = DrugDiseaseStudy.objects.filter(drug_bankID__drug_bankID=drug)
        if len(diseases) > 0:
            for disease in diseases:
                results.append(disease.disease_name.disease_name)
    # print("atc related search, result = ", results)

    return JsonResponse({'suggestions': results})
