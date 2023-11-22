import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'conf.settings')
django.setup()

# First, import the necessary models and functions
from drug.models import Drug, DrugAtcAssociation, AtcChemicalSubstance, AtcPharmacologicalGroup, AtcTherapeuticGroup, AtcAnatomicalGroup, AtcChemicalGroup

# Specify the drug of interest
drug_name = "Insulin human"

# Retrieve the drug object based on the name
drug = Drug.objects.get(name=drug_name)

print("Drug: ", drug)

# Get the related ATC code of the drug
atc_code = DrugAtcAssociation.objects.filter(drug_id=drug).values_list('atc_id_id')


print("atc_code = ", atc_code, " length = ", len(atc_code))

# # Retrieve the related ATC codes in 5 levels
# atc_chemical_substance = AtcChemicalSubstance.objects.get(id=atc_code.id[:7])
# atc_chemical_group = AtcChemicalGroup.objects.get(id=atc_code.id[:5])
# atc_pharmacological_group = AtcPharmacologicalGroup.objects.get(id=atc_code.id[:4])
# atc_therapeutic_group = AtcTherapeuticGroup.objects.get(id=atc_code.id[:3])
# atc_anatomical_group = AtcAnatomicalGroup.objects.get(id=atc_code.id[:1])

# print("atc_chemical_substance = ", atc_chemical_substance)
# print("atc_chemical_group = ", atc_chemical_group)
# print("atc_pharmacological_group = ", atc_pharmacological_group)
# print("atc_therapeutic_group = ", atc_therapeutic_group)
# print("atc_anatomical_group = ", atc_anatomical_group)


# # Retrieve the drugs that belong to each ATC code level
# atc_chemical_substance_drugs = DrugAtcAssociation.objects.filter(atc_id__id__startswith=atc_chemical_substance.id).values_list('drug_id__name')
# atc_pharmacological_group_drugs = DrugAtcAssociation.objects.filter(atc_id__id__startswith=atc_pharmacological_group.id).values_list('drug_id__name')
# atc_therapeutic_group_drugs = DrugAtcAssociation.objects.filter(atc_id__id__startswith=atc_therapeutic_group.id).values_list('drug_id__name')
# atc_anatomical_group_drugs = DrugAtcAssociation.objects.filter(atc_id__id__startswith=atc_anatomical_group.id).values_list('drug_id__name')


# # Print the results
# print(f"Related ATC code of drug {drug_name}: {atc_code}")
# print(f"ATC Chemical Substance: {atc_chemical_substance}")
# print(f"Drugs in ATC Chemical Substance: {atc_chemical_substance_drugs}")
# print(f"ATC Pharmacological Group: {atc_pharmacological_group}")
# print(f"Drugs in ATC Pharmacological Group: {atc_pharmacological_group_drugs}")
# print(f"ATC Therapeutic Group: {atc_therapeutic_group}")
# print(f"Drugs in ATC Therapeutic Group: {atc_therapeutic_group_drugs}")
# print(f"ATC Anatomical Group: {atc_anatomical_group}")
# print(f"Drugs in ATC Anatomical Group: {atc_anatomical_group_drugs}")
