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
from disease.models import DrugDiseaseStudy, Disease


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
        # if len(drugs) > 0:
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
        # if len(drugs) > 0:
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
        # if len(drugs) > 0:
        dd[c] = round(len(list(set(data))) / len(drugs), 1)
total=0
for k in dd.keys():
    total+=dd.get(k)
print("GenebassPGx pLoF: \n" , total)


#-------------------------------------- Count disease classes for stacked heatmap
#-------------------------------------- 
#-------------------------------------- 
#count for associations on a condition from Pharmgkb with stacked heatmap
#because we plot the stacked heatmap based on the histogram of pharmgkb association counts
total_pharmgkb_association_count = {} # after calculation: {'A': 333, 'B': 601, 'C': 398, 'D': 490, 'G': 86, 'H': 3, 'J': 329, 'L': 1237, 'M': 168, 'N': 904, 'P': 14, 'R': 213, 'S': 86, 'V': 42}
with open("Data/circos-0.69-9/data/atc/PharmgKB_0.05_data.txt", "r") as f:
    lines = f.readlines()
    for line in lines:
        group = line.split()[0][4]
        value = line.split()[3]
        total_pharmgkb_association_count[group]=total_pharmgkb_association_count.get(group,0) + int(value)

dd={}
distinct_disease_classes = ['Behavior Mechanisms', 'Cardiovascular', 'Chemically-Induced Disorders', 'Congenital and Neonatal', 'Digestive System', 'Endocrine System', 'Eye Diseases', 'Female Urogenital', 'Genetic, Inborn', 'Hemic and Lymphatic', 'Immune System', 'Infections', 'Male Urogenital', 'Mental Disorders', 'Musculoskeletal', 'Neoplasms', 'Nervous System', 'Nutritional and Metabolic', 'Occupational Diseases', 'Otorhinolaryngologic', 'Pathological Conditions', 'Respiratory Tract', 'Skin and Connective Tissue', 'Stomatognathic', 'Wounds and Injuries']
total_disease_count = {}
total_label = 0 
for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
    total=0
    l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
    print("len l", len(l))
    total_label = total_label + len(l)
    l = sorted(l) #list of "S03", "V03"...
    for c in l:
        disease_class_count = {}
        #count the number of drugs in the atc codes starting with "S03", ...
        drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
        if len(drugs)>0:
            disease_classes = DrugDiseaseStudy.objects.filter(Q(drug_bankID__in=drugs)&Q(clinical_trial="4")).values_list("disease_name__disease_class", flat=True)
            print(c," disease class ", len(disease_classes))
            if len(disease_classes)>0:
                for disease_class in disease_classes:
                    disease_class_count[disease_class] = disease_class_count.get(disease_class, 0) + 1
                    total_disease_count[c]=total_disease_count.get(c, 0) + 1
            else:
                for disease_class in distinct_disease_classes:
                    disease_class_count[disease_class] = 0
                total_disease_count[c] = 0
        else:
            for disease_class in distinct_disease_classes:
                disease_class_count[disease_class] = 0
            total_disease_count[c] = 0
        arranged_dict = {}
        for di in distinct_disease_classes:
            arranged_dict[di] = disease_class_count.get(di,0)
        dd[c] = arranged_dict

for key in dd:
    print(key)
    my_dict = dd.get(key)
    print(my_dict)
    sorted_dict = {k: v for k, v in sorted(my_dict.items(), key=lambda item: item[1], reverse=True)}
    dd[key] = sorted_dict



#put the data into file to create stacked histogram
with open("Data/circos-0.69-9/data/atc/PharmgKB_0.05_data.txt", "r") as f:
    with open("Data/circos-0.69-9/data/atc/PharmgKB_0.05_data_stacked_histogram.txt", "w") as ff:
        lines = f.readlines()
        groups = list(dd.keys())
        for line, group in zip(lines, groups):
            print(line," ", group)
            range = int(line.split()[3])
            print("range: ", range)
            
            ff.write(line.split()[0]+"\t"+line.split()[1]+"\t"+line.split()[2]+"\t")
            for v in dd.get(group).values():
                if total_disease_count.get(group)>0:
                    ff.write(str(v*1.0*range/total_disease_count.get(group))+",")
                else:
                    ff.write(str(0)+",")
            ff.write("\n")

#put the data into file to create stacked histogram for trial 4
with open("Data/circos-0.69-9/data/atc/PharmgKB_0.05_data.txt", "r") as f:
    with open("Data/circos-0.69-9/data/atc/PharmgKB_0.05_data_stacked_histogram_trial_4.txt", "w") as ff:
        lines = f.readlines()
        groups = list(dd.keys())
        for line, group in zip(lines, groups):
            print(line," ", group)
            range = int(line.split()[3])
            print("range: ", range)
            
            ff.write(line.split()[0]+"\t"+line.split()[1]+"\t"+line.split()[2]+"\t")
            for v in dd.get(group).values():
                if total_disease_count.get(group)>0:
                    ff.write(str(v*1.0*range/total_disease_count.get(group))+",")
                else:
                    ff.write(str(0)+",")
            ff.write("\n")

