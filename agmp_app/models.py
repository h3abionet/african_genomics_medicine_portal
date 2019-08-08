from django.db import models
from django.utils import timezone
from decimal import Decimal

# Create your models here.    
class drug_state(models.Model):
    state_id=models.AutoField(primary_key=True)
    state_name=models.CharField(max_length=250)

class drug(models.Model):
    drug_id=models.AutoField(primary_key=True)
    drug_name=models.CharField(max_length=250)
    posology=models.CharField(max_length=250, default="NA")
    chemical_structure=models.TextField(default="NA")
    state=models.ForeignKey(drug_state, on_delete=models.CASCADE)
    drug_bank_id=models.IntegerField(default=0) #may have to link to another table

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
    protein=models.CharField(max_length=50, default="NA")
    function=models.TextField(default="NA")

class country_ethnicity(models.Model):
    id=models.AutoField(primary_key=True)
    country_ethnicity=models.CharField(max_length=150)

#we may have to change disease_phenotype to just phenotype
#since some of the phenotypes we look at there are not necessarily diseases
class snp(models.Model):
    snp_id=models.AutoField(primary_key=True)
    rs_id=models.CharField(max_length=50)
    drug=models.ForeignKey(drug, on_delete=models.CASCADE, default=1)
    allele=models.CharField(max_length=50)
    gene=models.ForeignKey(pharmacogenes, on_delete=models.CASCADE,default=2)
    disease_phenotype=models.TextField()
    reference=models.ForeignKey(study, on_delete=models.CASCADE,default=3)
    chromosome=models.CharField(max_length=50)
    p_value=models.DecimalField(max_digits=10,decimal_places=4,default=Decimal('0.0000'))

class snp_country_ethnicity(models.Model):
    id=models.AutoField(primary_key=True)
    snp_id=models.ForeignKey(snp, on_delete=models.CASCADE)
    country_ethnicity_id=models.ForeignKey(country_ethnicity, on_delete=models.CASCADE)

class star_allele(models.Model):
    id=models.AutoField(primary_key=True)
    star_annotation=models.CharField(max_length=50)
    drug=models.ForeignKey(drug, on_delete=models.CASCADE)
    gene=models.ForeignKey(pharmacogenes, on_delete=models.CASCADE)
    disease_phenotype=models.CharField(max_length=50)
    reference=models.ForeignKey(study, on_delete=models.CASCADE)
    chromosome=models.CharField(max_length=50)
    p_value=models.DecimalField(max_digits=10,decimal_places=4,default=Decimal('0.0000'))
  
class star_allele_ethnicity_country(models.Model):
    id=models.AutoField(primary_key=True)
    star_allele_id=models.ForeignKey(star_allele, on_delete=models.CASCADE)
    country_ethnicity_id=models.ForeignKey(country_ethnicity, on_delete=models.CASCADE)


