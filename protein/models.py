from django.db import models

# Create your models here.


class Protein(models.Model):
    uniprot_ID = models.CharField(max_length=50, primary_key=True)
    genename = models.TextField()  # string values
    geneID = models.CharField(max_length=50)  # string values
    entry_name = models.TextField()  # long string values
    protein_name = models.TextField()  # long string values
    sequence = models.TextField(null=True)
    af_pdb = models.TextField(null=True)
    Protein_class = models.TextField(null=True)

    class Meta():
        ordering = ('uniprot_ID',)

    def __str__(self):
        return "Protein with UniProt ID: " + self.uniprot_ID + " and genename: " + self.genename
    
class Structure(models.Model):
    uniprot_ID = models.ForeignKey(Protein, on_delete=models.CASCADE)
    primary_struc = models.TextField()
    tertiary_struc = models.TextField()

    

class Species(models.Model):
    latin_name = models.CharField(max_length=100, unique=True)
    common_name = models.CharField(max_length=100, blank=True)

    def __str__(self):
        return self.latin_name

    class Meta():
        db_table = 'species'
