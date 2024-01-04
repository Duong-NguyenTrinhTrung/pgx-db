from django.db import models
from drug.models import Drug

# Create your models here.
# 'Disease_name', 'Disease_class', 'Phase', 'Merged_RefNew',
# 'Standard_inchiKey', 'Disease_UML_CUI', 'CID', 'DrugBank_ID'


class Disease(models.Model):
    disease_name = models.CharField(max_length=100)
    disease_class = models.CharField(max_length=100)
    link = models.TextField() 
    standard_inchiKey = models.TextField() 
    disease_UML_CUI = models.CharField(max_length=255)
    clinical_trial = models.CharField(max_length=10)
    drug_bankID = models.ForeignKey(
        "drug.drug", on_delete=models.CASCADE)