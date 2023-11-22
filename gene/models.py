from django.db import models

# Create your models here.


class Gene(models.Model):
    gene_id = models.CharField(max_length=50, primary_key=True)
    genename = models.CharField(max_length=50)  # string values
    primary_transcript = models.CharField(max_length=50)  # string values
