from drug.models import (Drug,
    AtcTherapeuticGroup,
    AtcPharmacologicalGroup,
    DrugAtcAssociation,
)
from django.db.models import Q
with open("Data/circos-0.69-9/Data/atc/sublayer-l3-drug-clinical-status.txt", "w") as f:
    for cli in [0, 1, 2, 3, 4, 5]:
        for ch in ["A", "B", "C","D","G","H","J","L","M","N","P","R","S","V"]:
            l = list(AtcPharmacologicalGroup.objects.filter(id__istartswith=ch).values_list("id", flat=True))
            for c in l:
                count = DrugAtcAssociation.objects.filter(Q(atc_id__id__startswith=c) & Q(drug_id__Clinical_status=cli)).count()
                if count>0:
                    print(c, " , clinical status ", cli, " ", count )
                    f.write(c + " , clinical status " + str(cli)+ " "+ str(count)+"\n")
                            