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


def sort_alpha_numeric(strings):
    def alphanumeric_key(string):
        # Split the string into the alphabetical and numeric parts
        parts = re.match(r"([a-zA-Z]+)(\d+)", string).groups()
        return [parts[0], int(parts[1])]
    return sorted(strings, key=alphanumeric_key)


#count data on genebass-pgx from level 3
#distinct annotation ['missense|LC', 'pLoF', 'pLoF|missense|LC', 'synonymous']
#range used in the main ideogram
d = {"A": 294,
    "B": 128,
    "C": 306,
    "D": 173,
    "G": 184,
    "H": 66, 
    "J": 229,
    "L": 298,
    "M": 134,
    "N": 369,
    "P": 50, 
    "R": 183,
    "S": 183,
    "V": 96,}

colors=["green", "orange", "deeppink", "darkviolet"]
prev_group=""

#count for associations on a condition from Pharmgkb
dd={}
with open("Data/circos-0.69-9/Data/atc/l3-text.txt", "w") as f:
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
                        P_Value_numeric__gte=0.01
                    )
                    if qs.count()>0:
                        print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                    for q in qs:
                        data.append(q)
            dd[c] = len(list(set(data)))
print(dd)
total=0
for k in dd.keys():
    total+=dd.get(k)
print(total)

#GenebassPGx
dd={}
with open("Data/circos-0.69-9/Data/atc/l3-text.txt", "w") as f:
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
                        Pvalue__gte=0.05,
                        annotation="synonymous",
                    )
                    if qs.count()>0:
                        print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                    for q in qs:
                        data.append(q)
            dd[c] = len(list(set(data)))
print(dd)
total=0
for k in dd.keys():
    total+=dd.get(k)
print(total)


#GenebassVariantPGx
dd={}
with open("Data/circos-0.69-9/Data/atc/l3-text.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        total=0
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            data = []
            #count the number of drugs in the atc codes starting with "S03", ...
            drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
            for drug in drugs:
                genes = (list(Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID_id__genename", flat=True)))
                for gene in genes:
                    qs = GenebassVariantPGx.objects.filter(
                        drugbank_id=drug,
                        genename=gene,
                        # Pvalue__isnull=False,
                        Pvalue__gte=0.05,
                        annotation="synonymous",
                    )
                    if qs.count()>0:
                        print(c, " ", drug, " ", gene, " ", " len qs ", qs.count())
                    for q in qs:
                        data.append(q)
            dd[c] = len(list(set(data)))
print(dd)
total=0
for k in dd.keys():
    total+=dd.get(k)
print(total)





# def convert(x, r, rr):
#     return int(x*r/rr)

# # colors=["green", "orange", "deeppink", "darkviolet"]
# prev_group=""
# with open("Data/circos-0.69-9/Data/atc/l3-text-pharmgkb.txt", "w") as f:
#     for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
#         total=0
#         l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
#         l = sorted(l) #list of "S03", "V03"...
#         for c in l:
#             #count the number of drugs in the atc codes starting with "S03", ...
#             drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
#             count=len(list(set(list(Pharmgkb.objects.filter(drugbank_id__in=drugs)))))
#             r = d.get(c[0]) #destination range
#             rr = dd.get(c[0])# current range
#             if c[0]!=prev_group:
#                 start=0
#                 f.write("name"+c[0] + "\t" +str(start) + "\t" + str(convert(count, r, rr))+ "\t" + c + "\n")
#             else:
#                 f.write("name"+c[0] + "\t" +str(convert(start, r, rr)) + "\t" + str(convert(start+count, r, rr))+ "\t" + c + "\n")
#             start=start+count+1
#             prev_group=c[0]


# prev_group=""
# with open("Data/circos-0.69-9/Data/atc/l3-data-pharmgkb.txt", "w") as f:
#     for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
#         total=0
#         l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
#         l = sorted(l) #list of "S03", "V03"...
#         for c in l:
#             #count the number of drugs in the atc codes starting with "S03", ...
#             drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
#             count=len(list(set(list(Pharmgkb.objects.filter(drugbank_id__in=drugs)))))
#             r = d.get(c[0]) #destination range
#             rr = dd.get(c[0])# current range
#             if c[0]!=prev_group:
#                 start=0
#                 f.write("name"+c[0] + "\t" +str(start) + "\t" + str(convert(count, r, rr))+ "\t" + str(convert(count, r, rr)) + "\n")
#             else:
#                 f.write("name"+c[0] + "\t" +str(convert(start, r, rr)) + "\t" + str(convert(start+count, r, rr))+ "\t" + str(convert(count, r, rr))+ "\n")
#             start=start+count+1
#             prev_group=c[0]


# dd={}
# with open("Data/circos-0.69-9/Data/atc/l3-text-genebased.txt", "w") as f:
#     for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
#         total=0
#         l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
#         l = sorted(l) #list of "S03", "V03"...
#         for c in l:
#             #count the number of drugs in the atc codes starting with "S03", ...
#             drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
#             count=len(list(set(list(GenebassPGx.objects.filter(drugbank_id__in=drugs)))))
#             total+=count
#         dd[ch]=total
# dd={'A': 398013, 'B': 68327, 'C': 829472, 'D': 136426, 'G': 170683, 'H': 56852, 'J': 79516, 'L': 56872, 'M': 239052, 'N': 545652, 'P': 22760, 'R': 261448, 'S': 204628, 'V': 22784}

# prev_group=""
# with open("Data/circos-0.69-9/Data/atc/l3-text-genebased.txt", "w") as f:
#     for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
#         total=0
#         l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
#         l = sorted(l) #list of "S03", "V03"...
#         for c in l:
#             #count the number of drugs in the atc codes starting with "S03", ...
#             drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
#             count=len(list(set(list(GenebassPGx.objects.filter(drugbank_id__in=drugs)))))
#             r = d.get(c[0]) #destination range
#             rr = dd.get(c[0])# current range
#             if c[0]!=prev_group:
#                 start=0
#                 f.write("name"+c[0] + "\t" +str(start) + "\t" + str(convert(count, r, rr))+ "\t" + c + "\n")
#             else:
#                 f.write("name"+c[0] + "\t" +str(convert(start, r, rr)) + "\t" + str(convert(start+count, r, rr))+ "\t" + c + "\n")
#             start=start+count+1
#             prev_group=c[0]


# dd={}
# with open("Data/circos-0.69-9/Data/atc/l3-text-variantbased.txt", "w") as f:
#     for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
#         print(ch)
#         total=0
#         l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
#         l = sorted(l) #list of "S03", "V03"...
#         for c in l:
#             #count the number of drugs in the atc codes starting with "S03", ...
#             drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
#             count=len(list(set(list(GenebassVariantPGx.objects.filter(drugbank_id__in=drugs)))))
#             total+=count
#         dd[ch]=total

# dd = {'A': 41554674, 'B': 6671214, 'C': 89914681, 'D': 14724172, 'G': 18376425, 'H': 6142652, 'J': 8604150, 'L': 6137256, 'M': 25719937, 'N': 58726283, 'P': 2459590, 'R': 28265442, 'S': 21819756, 'V': 2466221}

# prev_group=""
# with open("Data/circos-0.69-9/Data/atc/l3-text-genebased.txt", "w") as f:
#     for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
#         total=0
#         l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
#         l = sorted(l) #list of "S03", "V03"...
#         for c in l:
#             #count the number of drugs in the atc codes starting with "S03", ...
#             drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
#             count=len(list(set(list(GenebassVariantPGx.objects.filter(drugbank_id__in=drugs)))))
#             r = d.get(c[0]) #destination range
#             rr = dd.get(c[0])# current range
#             if c[0]!=prev_group:
#                 start=0
#                 f.write("name"+c[0] + "\t" +str(start) + "\t" + str(convert(count, r, rr))+ "\t" + c + "\n")
#             else:
#                 f.write("name"+c[0] + "\t" +str(convert(start, r, rr)) + "\t" + str(convert(start+count, r, rr))+ "\t" + c + "\n")
#             start=start+count+1
#             prev_group=c[0]