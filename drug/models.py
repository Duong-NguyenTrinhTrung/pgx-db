# drug
from django.db import models
# Create your models here.


class AtcAnatomicalGroup(models.Model):
    id = models.CharField(max_length=1, primary_key=True)  
    name = models.CharField(max_length=100, default="None")
    class Meta():
        db_table = 'atc_anatomical_group'
        ordering = ('id',)
    def __str__(self):
        return self.id # + "_" + self.name

class AtcTherapeuticGroup(models.Model):
    id = models.CharField(max_length=3, primary_key=True)  
    parent = models.ForeignKey("drug.atcanatomicalgroup", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="None")
    class Meta():
        db_table = 'atc_therapeutic_group'
        ordering = ('id',)
    def __str__(self):
        return self.id # + "_" + self.name

class AtcPharmacologicalGroup(models.Model):
    id = models.CharField(max_length=4, primary_key=True)  
    parent = models.ForeignKey("drug.atctherapeuticgroup", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="None")
    class Meta():
        db_table = 'atc_pharmacological_group'
        ordering = ('id',)
    def __str__(self):
        return self.id # + "_" + self.name

class AtcChemicalGroup(models.Model):
    id = models.CharField(max_length=5, primary_key=True)  
    parent = models.ForeignKey("drug.atcpharmacologicalgroup", on_delete=models.CASCADE)
    name = models.CharField(max_length=100, default="None")
    class Meta():
        db_table = 'atc_chemical_group'
        ordering = ('id',)
    def __str__(self):
        return self.id  # + "_" + self.name
        
class AtcChemicalSubstance(models.Model):
    id = models.CharField(max_length=7, primary_key=True)  
    name = models.CharField(max_length=100, default="None")
    parent = models.ForeignKey("drug.atcchemicalgroup", on_delete=models.CASCADE)
    class Meta():
        db_table = 'atc_chemical_substance'
        ordering = ('id',)
    def __str__(self):
        return self.id # + "_" + self.name

class DrugAtcAssociation(models.Model):
    association_id = models.AutoField(auto_created=True, primary_key=True)
    atc_id = models.ForeignKey("drug.atcchemicalsubstance", on_delete=models.CASCADE)
    drug_id = models.ForeignKey("drug.drug", on_delete=models.CASCADE)
    class Meta():
        db_table = 'drug_atc_association'
        indexes = [
                    models.Index(fields=['atc_id']),
                    models.Index(fields=['drug_id']),
                ]

class DrugType(models.Model):
    drugtype = models.IntegerField(primary_key=True)  
    type_detail = models.CharField(max_length=20, default="None") # being either 'biotech' or 'small molecule' 

    class Meta():
        db_table = 'drugtype'

class DrugGroup(models.Model):
    druggroup = models.CharField(max_length=50, primary_key=True)  
    group_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'druggroup'

class DrugChembl(models.Model):
    drugchembl = models.CharField(max_length=50, primary_key=True)  
    chembl_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'drugchembl'

class DrugPubChemSubstance(models.Model):
    drugpubchemblsubstance = models.CharField(max_length=50, primary_key=True)  
    pubchemblsubstance_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'drugpubchemblsubstance'



class DrugClass(models.Model):
    drugclass = models.CharField(max_length=50, primary_key=True)  
    class_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'drugclass'

class DrugSubclass(models.Model):
    drugsubclass = models.CharField(max_length=50, primary_key=True)  
    subclass_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'drugsubclass'

class DrugSuperclass(models.Model):
    drugsuperclass = models.CharField(max_length=50, primary_key=True)  
    superclass_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'drugsuperclass'

class DrugParent(models.Model):
    drugparent = models.CharField(max_length=50, primary_key=True)  
    parent_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'drugparent'

class DrugCategory(models.Model):
    drugcategory = models.CharField(max_length=50, primary_key=True)  
    category_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'drugcategory'

class DrugPubChemCompound(models.Model):
    compound = models.CharField(max_length=50, primary_key=True)  
    compound_detail = models.TextField(default="None") 

    class Meta():
        db_table = 'drugpubchemcompound'

class Drug(models.Model):
    drug_bankID = models.CharField(max_length=20, primary_key=True)
    drugtype = models.ForeignKey(
        "drug.drugtype", on_delete=models.CASCADE)
    name = models.TextField()  # long string values
    groups = models.ForeignKey(
        "drug.druggroup", on_delete=models.CASCADE)
    categories = models.ForeignKey(
        "drug.drugcategory", on_delete=models.CASCADE)
    description = models.TextField()  # long string values
    aliases = models.TextField()  # similar to name
    superclass = models.ForeignKey(
        "drug.drugsuperclass", on_delete=models.CASCADE)
    classname = models.ForeignKey(
        "drug.drugclass", on_delete=models.CASCADE)
    subclass = models.ForeignKey(
        "drug.drugsubclass", on_delete=models.CASCADE)
    direct_parent = models.ForeignKey(
        "drug.drugparent", on_delete=models.CASCADE)
    indication = models.TextField()  # long string values
    pharmacodynamics = models.TextField()  # long string values
    moa = models.TextField()  # long string values
    absorption = models.TextField()  # long string values

    toxicity = models.TextField()  # long string values
    halflife = models.TextField()  # long string values
    distribution_volume = models.TextField()  # long string values
    protein_binding = models.TextField()  # long string values

    dosages = models.TextField()  # long string values
    properties = models.TextField()  # long string values

    chEMBL = models.ForeignKey(
        "drug.drugchembl", on_delete=models.CASCADE)
    pubChemCompound = models.ForeignKey(
        "drug.drugpubchemcompound", on_delete=models.CASCADE)
    pubChemSubstance = models.ForeignKey(
        "drug.drugpubchemsubstance", on_delete=models.CASCADE)
    
    Clinical_status = models.IntegerField(null=True)

    class Meta():
        ordering = ('drug_bankID',)
        indexes = [
                    models.Index(fields=['drug_bankID']),
                ]

class AdverseDrugReaction(models.Model):
    drug_bankID = models.ForeignKey(
        "drug.drug", on_delete=models.CASCADE)
    adr_data = models.TextField(default="None")

class SideEffect(models.Model):
    side_effect_name = models.CharField(max_length=255, primary_key=True)
    side_effect_definition = models.TextField()


class PreCachedDrugNetwork(models.Model):
    atc_code = models.CharField(max_length=7)
    drug_json_data = models.TextField(default="")
    protein_json_data = models.TextField(default="")
    general_json_data = models.TextField(default="")
    interaction_json_data = models.TextField(default="")