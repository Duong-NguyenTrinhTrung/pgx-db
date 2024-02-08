from variant.models import GenebassPGx
from drug.models import (Drug,
    AtcAnatomicalGroup,
    AtcTherapeuticGroup,
    AtcPharmacologicalGroup,
    DrugAtcAssociation,
)
from variant.models import Pharmgkb, GenebassVariantPGx
from interaction.models import Interaction
import math
import re
from django.db.models import Q

#count for associations on a condition from Pharmgkb
dd={}
for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
    total=0
    l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
    l = sorted(l) #list of "S03", "V03"...
    for c in l:
        data = []
        #count the number of drugs in the atc codes starting with "S03", ...
        drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
        for drug in drugs:
            genes = (list(Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID_id__geneID", flat=True)))
            for gene in genes:
                qs = Pharmgkb.objects.filter(
                    drugbank_id=drug,
                    geneid=gene,
                    P_Value__isnull=False,
                    # P_Value__startswith="=",
                    P_Value_numeric__lte=0.05
                )
                # if qs.count()>0:
                #     print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                for q in qs:
                    data.append(q)
        dd[c] = len(list(set(data)))
total=0
for k in dd.keys():
    total+=dd.get(k)
print("PharmgKB \n", total)
#GenebassPGx missense
dd={}
for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
    total=0
    l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
    l = sorted(l) #list of "S03", "V03"...
    for c in l:
        data = []
        #count the number of drugs in the atc codes starting with "S03", ...
        drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
        for drug in drugs:
            genes = (list(Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID_id__geneID", flat=True)))
            for gene in genes:
                qs = GenebassPGx.objects.filter(
                    drugbank_id=drug,
                    gene_id=gene,
                    # Pvalue__isnull=False,
                    Pvalue__lte=0.05,
                    annotation="missense|LC",
                )
                # if qs.count()>0:
                #     print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                for q in qs:
                    data.append(q)
        dd[c] = len(list(set(data)))
total=0
for k in dd.keys():
    total+=dd.get(k)
print("GenebassPGx missense: \n" , total)
#GenebassPGx pLoF
dd={}
for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
    total=0
    l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
    l = sorted(l) #list of "S03", "V03"...
    for c in l:
        data = []
        #count the number of drugs in the atc codes starting with "S03", ...
        drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
        for drug in drugs:
            genes = (list(Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID_id__geneID", flat=True)))
            for gene in genes:
                qs = GenebassPGx.objects.filter(
                    drugbank_id=drug,
                    gene_id=gene,
                    # Pvalue__isnull=False,
                    Pvalue__lte=0.05,
                    annotation="pLoF",
                )
                # if qs.count()>0:
                #     print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                for q in qs:
                    data.append(q)
        dd[c] = len(list(set(data)))
total=0
for k in dd.keys():
    total+=dd.get(k)
print("GenebassPGx pLoF: \n" , total)

#-------------------------------------- NORMALIZATION BY DRUGS
#--------------------------------------
#--------------------------------------
#--------------------------------------
#count for associations on a condition from Pharmgkb
dd={}
for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
    total=0
    l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
    l = sorted(l) #list of "S03", "V03"...
    for c in l:
        data = []
        #count the number of drugs in the atc codes starting with "S03", ...
        drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
        for drug in drugs:
            genes = (list(Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID_id__geneID", flat=True)))
            for gene in genes:
                qs = Pharmgkb.objects.filter(
                    drugbank_id=drug,
                    geneid=gene,
                    P_Value__isnull=False,
                    # P_Value__startswith="=",
                    P_Value_numeric__lte=0.05
                )
                # if qs.count()>0:
                #     print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                for q in qs:
                    data.append(q)
        if len(drugs) > 0:
            dd[c] = round(len(list(set(data))) / len(drugs), 1)

total=0
for k in dd.keys():
    total+=dd.get(k)
print("PharmgKB \n", total) # --> 117


#GenebassPGx missense
dd={}
for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
    total=0
    l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
    l = sorted(l) #list of "S03", "V03"...
    for c in l:
        data = []
        #count the number of drugs in the atc codes starting with "S03", ...
        drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
        for drug in drugs:
            genes = (list(Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID_id__geneID", flat=True)))
            for gene in genes:
                qs = GenebassPGx.objects.filter(
                    drugbank_id=drug,
                    gene_id=gene,
                    # Pvalue__isnull=False,
                    Pvalue__lte=0.05,
                    annotation="missense|LC",
                )
                # if qs.count()>0:
                #     print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                for q in qs:
                    data.append(q)
        if len(drugs) > 0:
            dd[c] = round(len(list(set(data))) / len(drugs), 1)
total=0
for k in dd.keys():
    total+=dd.get(k)
print("GenebassPGx missense: \n" , total)

#GenebassPGx pLoF
dd={}
for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
    total=0
    l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
    l = sorted(l) #list of "S03", "V03"...
    for c in l:
        data = []
        #count the number of drugs in the atc codes starting with "S03", ...
        drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
        for drug in drugs:
            genes = (list(Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID_id__geneID", flat=True)))
            for gene in genes:
                qs = GenebassPGx.objects.filter(
                    drugbank_id=drug,
                    gene_id=gene,
                    # Pvalue__isnull=False,
                    Pvalue__lte=0.05,
                    annotation="pLoF",
                )
                # if qs.count()>0:
                #     print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                for q in qs:
                    data.append(q)
        if len(drugs) > 0:
            dd[c] = round(len(list(set(data))) / len(drugs), 1)
total=0
for k in dd.keys():
    total+=dd.get(k)
print("GenebassPGx pLoF: \n" , total)

