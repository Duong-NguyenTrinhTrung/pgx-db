from variant.models import GenebassPGx
from drug.models import (Drug,
    AtcAnatomicalGroup,
    AtcTherapeuticGroup,
    AtcPharmacologicalGroup,
    DrugAtcAssociation,
)
from variant.models import Pharmgkb, GenebassVariantPGx
import math
import re
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
#dd hold the total pharmgkb associations for each Anatomical group
dd={}
with open("Data/circos-0.69-9/Data/atc/l3-text.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        total=0
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
            count=len(list(set(list(Pharmgkb.objects.filter(drugbank_id__in=drugs)))))
            total+=count
        dd[ch]=total
# print(dd) 
#{'A': 1123, 'B': 1275, 'C': 2502, 'D': 1101, 'G': 242, 'H': 12, 'J': 759, 'L': 3226, 'M': 451, 'N': 3905, 'P': 48, 'R': 528, 'S': 260, 'V': 354}
{'A': 1121, 'B': 1275, 'C': 1266, 'D': 1091, 'G': 235, 'H': 12, 'J': 754, 'L': 3206, 'M': 451, 'N': 3797, 'P': 48, 'R': 501, 'S': 231, 'V': 354}

def convert(x, r, rr):
    return int(x*r/rr)

# colors=["green", "orange", "deeppink", "darkviolet"]
prev_group=""
with open("Data/circos-0.69-9/Data/atc/l3-text-pharmgkb.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        total=0
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
            count=len(list(set(list(Pharmgkb.objects.filter(drugbank_id__in=drugs)))))
            r = d.get(c[0]) #destination range
            rr = dd.get(c[0])# current range
            if c[0]!=prev_group:
                start=0
                f.write("name"+c[0] + "\t" +str(start) + "\t" + str(convert(count, r, rr))+ "\t" + c + "\n")
            else:
                f.write("name"+c[0] + "\t" +str(convert(start, r, rr)) + "\t" + str(convert(start+count, r, rr))+ "\t" + c + "\n")
            start=start+count+1
            prev_group=c[0]


prev_group=""
with open("Data/circos-0.69-9/Data/atc/l3-data-pharmgkb.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        total=0
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
            count=len(list(set(list(Pharmgkb.objects.filter(drugbank_id__in=drugs)))))
            r = d.get(c[0]) #destination range
            rr = dd.get(c[0])# current range
            if c[0]!=prev_group:
                start=0
                f.write("name"+c[0] + "\t" +str(start) + "\t" + str(convert(count, r, rr))+ "\t" + str(convert(count, r, rr)) + "\n")
            else:
                f.write("name"+c[0] + "\t" +str(convert(start, r, rr)) + "\t" + str(convert(start+count, r, rr))+ "\t" + str(convert(count, r, rr))+ "\n")
            start=start+count+1
            prev_group=c[0]


dd={}
with open("Data/circos-0.69-9/Data/atc/l3-text-genebased.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        total=0
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
            count=len(list(set(list(GenebassPGx.objects.filter(drugbank_id__in=drugs)))))
            total+=count
        dd[ch]=total
dd={'A': 398013, 'B': 68327, 'C': 829472, 'D': 136426, 'G': 170683, 'H': 56852, 'J': 79516, 'L': 56872, 'M': 239052, 'N': 545652, 'P': 22760, 'R': 261448, 'S': 204628, 'V': 22784}

prev_group=""
with open("Data/circos-0.69-9/Data/atc/l3-text-genebased.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        total=0
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
            count=len(list(set(list(GenebassPGx.objects.filter(drugbank_id__in=drugs)))))
            r = d.get(c[0]) #destination range
            rr = dd.get(c[0])# current range
            if c[0]!=prev_group:
                start=0
                f.write("name"+c[0] + "\t" +str(start) + "\t" + str(convert(count, r, rr))+ "\t" + c + "\n")
            else:
                f.write("name"+c[0] + "\t" +str(convert(start, r, rr)) + "\t" + str(convert(start+count, r, rr))+ "\t" + c + "\n")
            start=start+count+1
            prev_group=c[0]


dd={}
with open("Data/circos-0.69-9/Data/atc/l3-text-variantbased.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        print(ch)
        total=0
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
            count=len(list(set(list(GenebassVariantPGx.objects.filter(drugbank_id__in=drugs)))))
            total+=count
        dd[ch]=total

dd = {'A': 41554674, 'B': 6671214, 'C': 89914681, 'D': 14724172, 'G': 18376425, 'H': 6142652, 'J': 8604150, 'L': 6137256, 'M': 25719937, 'N': 58726283, 'P': 2459590, 'R': 28265442, 'S': 21819756, 'V': 2466221}

prev_group=""
with open("Data/circos-0.69-9/Data/atc/l3-text-genebased.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        total=0
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
            count=len(list(set(list(GenebassVariantPGx.objects.filter(drugbank_id__in=drugs)))))
            r = d.get(c[0]) #destination range
            rr = dd.get(c[0])# current range
            if c[0]!=prev_group:
                start=0
                f.write("name"+c[0] + "\t" +str(start) + "\t" + str(convert(count, r, rr))+ "\t" + c + "\n")
            else:
                f.write("name"+c[0] + "\t" +str(convert(start, r, rr)) + "\t" + str(convert(start+count, r, rr))+ "\t" + c + "\n")
            start=start+count+1
            prev_group=c[0]