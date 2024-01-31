from drug.models import (Drug,
    AtcAnatomicalGroup,
    AtcTherapeuticGroup,
    AtcPharmacologicalGroup,
    DrugAtcAssociation,
)
from django.db.models import Q
with open("Data/circos-0.69-9/Data/atc/l1-main-ideogram.txt", "w") as f:
        f.write("#  chr - CHRNAME CHRLABEL START END COLOR\n")
        f.write("#  example: chr - nameA A 0 422 red\n")
        for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
            for c in ch:
                count = DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).distinct('drug_id').count()
                if count>0:
                    # print(c, " ", count )
                    f.write("chr - name"+c + "\t" +c +"\t0\t" + str(count)+ "\tred\n")
                            

