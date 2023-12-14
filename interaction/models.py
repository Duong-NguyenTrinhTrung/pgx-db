# interaction
from django.db import models
from drug.models import Drug
from protein.models import Protein

# Create your models here.
class Interaction(models.Model):
    interaction_id = models.AutoField(auto_created=True, primary_key=True)
    drug_bankID = models.ForeignKey(
        "drug.Drug", on_delete=models.CASCADE)
    uniprot_ID = models.ForeignKey(
        "protein.Protein", on_delete=models.CASCADE)
    actions = models.TextField()  
    known_action = models.TextField()  
    interaction_type = models.CharField(
        max_length=100
    )  
    pubmed_ids = models.TextField(default="None")

    class Meta:
        ordering = ["drug_bankID__name"]

    def __str__(self):
        return self.uniprot_ID.uniprot_ID + " acts as a " + self.interaction_type + " for drug " + self.drug_bankID.drug_bankID
    

# class Pgx(models.Model):
#     pgx_id = models.AutoField(auto_created=True, primary_key=True)
#     drug_bankID = models.ForeignKey("drug.Drug", on_delete=models.CASCADE)
#     gene_id = models.ForeignKey("gene.Gene", on_delete=models.CASCADE)
#     phenocode = models.ForeignKey("variant.VariantPhenocode", on_delete=models.CASCADE)
#     pgx_gb = models.TextField() 
#     pgx_ph = models.TextField() 