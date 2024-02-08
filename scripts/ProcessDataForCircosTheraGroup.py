from drug.models import (Drug,
    AtcAnatomicalGroup,
    AtcTherapeuticGroup,
    AtcPharmacologicalGroup,
    DrugAtcAssociation,
)
from django.db.models import Q

import re
def sort_alpha_numeric(strings):
    def alphanumeric_key(string):
        # Split the string into the alphabetical and numeric parts
        parts = re.match(r"([a-zA-Z]+)(\d+)", string).groups()
        return [parts[0], int(parts[1])]
    return sorted(strings, key=alphanumeric_key)


                    
#l2 text -> ok, not need for change
with open("Data/circos-0.69-9/Data/atc/l2-text.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        color="black"
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            count = DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).distinct('drug_id').count()
            if c.endswith("01"):
                start=0
                f.write("name"+c[0] + "\t" +str(start) + "\t" + str(count)+ "\t" + c +"\tcolor="+color + "\n")
            else:
                f.write("name"+c[0] + "\t" +str(start) + "\t" + str(start+count)+ "\t" + c+ "\tcolor="+color + "\n")
            start=start+count+1
            if color=="black":
                color="grey"
            else:
                color="black"

#l2 data -> ok, not need for change
with open("Data/circos-0.69-9/Data/atc/l2-data.txt", "w") as f:
    for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
        l = list(AtcTherapeuticGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
        l = sorted(l) #list of "S03", "V03"...
        for c in l:
            #count the number of drugs in the atc codes starting with "S03", ...
            count = DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).distinct('drug_id').count()
            if c.endswith("01"):
                start=0
                f.write("name"+c[0] + "\t" +str(start) + "\t" + str(count)+ "\t" + str(count)  + "\n")
            else:
                f.write("name"+c[0] + "\t" +str(start) + "\t" + str(start+count)+ "\t" + str(count)+ "\t" + "\n")
            start=start+count+1
                                                    