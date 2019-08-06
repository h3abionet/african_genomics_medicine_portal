from django.db import models
from django.utils import timezone

# Create your models here.    
class drug_state(models.Model):
    state_id=models.AutoField(primary_key=True)
    state_name=models.CharField(max_length=250)

class drug(models.Model):
    drug_id=models.AutoField(primary_key=True)
    drug_name=models.CharField(max_length=250)
    posology=models.CharField(max_length=250)
    chemical_structure=models.TextField()
    state_id=models.ForeignKey(drug_state, on_delete=models.CASCADE)
    drug_bank_id=models.IntegerField() #may have to link to another table

class externalid_type(models.Model):
    type_id=models.AutoField(primary_key=True)
    type_name=models.CharField(max_length=250)

class study(models.Model):
    study_id=models.AutoField(primary_key=True)
    study_title=models.CharField(max_length=250)
    #externalid_type=models.ForeignKey(externalid_type, on_delete=models.CASCADE) #we need to check if we really need this in here
    external_id=models.CharField(max_length=50)
    date=models.DateField(default=timezone.now) #we are using current date to hold this space, should change this when using real data

class pharmacogenes(models.Model):
    id=models.AutoField(primary_key=True)
    gene_name=models.CharField(max_length=50)
    protein=models.CharField(max_length=50)
    function=models.TextField()

class snp(models.Model):
    snp_id=models.AutoField(primary_key=True)
    rs_id=models.CharField(max_length=50)
    drug_id=models.ForeignKey(drug, on_delete=models.CASCADE, default=1)
    allele=models.CharField(max_length=50)
    gene_id=models.ForeignKey(pharmacogenes, on_delete=models.CASCADE,default=2)
    description=models.TextField()
    reference_id=models.ForeignKey(study, on_delete=models.CASCADE,default=3)
    #ethnicity_country_id=models.ForeignKey(ethnicity_country, on_delete=models.CASCADE)

class star_allele(models.Model):
    id=models.AutoField(primary_key=True)
    star_annotation=models.CharField(max_length=50)
    drug_id=models.ForeignKey(drug, on_delete=models.CASCADE)
    gene_id=models.ForeignKey(pharmacogenes, on_delete=models.CASCADE)
    disease_phenotype=models.CharField(max_length=50)
    reference_id=models.ForeignKey(study, on_delete=models.CASCADE)
    chromosome=models.CharField(max_length=50)
    disease_id=models.IntegerField()
