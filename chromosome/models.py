from django.db import models

# Create your models here.
class Chromosome(models.Model):
    genome_version = models.CharField(max_length=50)
    ensembl = models.CharField(max_length=50)  # string values
    ucsc = models.CharField(max_length=50)  # string values
    ncbi = models.CharField(max_length=50)  # string values
    refseq = models.CharField(max_length=50)  # string values
    gencode = models.CharField(max_length=50)  # string values
