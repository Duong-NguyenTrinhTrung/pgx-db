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

lowDrugHighAsso = ["D10", "D11", "J02", "L04", "R07"]
highDrugLowAsso = ["L01", "J01", "S01"]

for code in lowDrugHighAsso:
    drugs = list(set(list(DrugAtcAssociation.objects.filter(atc_id__id__startswith=c).values_list('drug_id', flat=True))))
    for drug in drugs:
        genes = (list(Interaction.objects.filter(drug_bankID=drug).values_list("uniprot_ID_id__geneID", flat=True)))