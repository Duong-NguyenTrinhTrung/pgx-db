from django.db import models
from drug.models import Drug

# Create your models here.
# 'Disease_name', 'Disease_class', 'Phase', 'Merged_RefNew',
# 'Standard_inchiKey', 'Disease_UML_CUI', 'CID', 'DrugBank_ID'


class Disease(models.Model):
    Disease_name = models.CharField(max_length=100)
    Disease_class = models.CharField(max_length=100)
    Merged_RefNew = models.CharField(max_length=255)
    CID = models.CharField(max_length=25)
    Standard_inchiKey = models.TextField() 
    Disease_UML_CUI = models.CharField(max_length=255)
    drug_bankID = models.ForeignKey(
        "drug.drug", on_delete=models.CASCADE)