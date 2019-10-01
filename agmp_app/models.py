from django.db import models
from django.utils import timezone
from decimal import Decimal


class drug(models.Model):
    id=models.CharField(max_length=250, primary_key=True)
    drug_name=models.CharField(max_length=250)
    drug_bank_id=models.IntegerField(default=0) #may have to link to another table
    #state=models.ForeignKey(drug_state, on_delete=models.CASCADE)
    state=models.CharField(max_length=250)
    indication=models.CharField(default="NA",max_length=50)
    iupac_name=models.CharField(default="NA",max_length=50)

class study(models.Model):
    id=models.CharField(max_length=250, primary_key=True)
    title=models.CharField(max_length=250)
    external_id=models.CharField(max_length=50)
    type=models.CharField(max_length=250)
    date=models.DateField(default=timezone.now) #we are using current date to hold this space, should change this when using real data

class pharmacogenes(models.Model):
    id=models.CharField(max_length=250, primary_key=True)
    gene_name=models.CharField(max_length=50, default="NA")
    protein=models.CharField(max_length=50, default="NA")
    function=models.TextField(default="NA",max_length=50)
    chromosome=models.CharField(default="NA",max_length=50)

class snp(models.Model):
    id=models.AutoField(primary_key=True)
    snp_id=models.CharField(max_length=50, default='NA')
    rs_id=models.CharField(max_length=50)
    drug=models.ForeignKey(drug, on_delete=models.CASCADE, default="DRUG1")
    allele=models.CharField(max_length=50)
    gene=models.ForeignKey(pharmacogenes, on_delete=models.CASCADE,default="PHARGENE19")
    phenotype=models.TextField()
    reference=models.ForeignKey(study, on_delete=models.CASCADE,default="REF1")
    p_value=models.CharField(max_length=10)
    #p_value=models.DecimalField(max_digits=10,decimal_places=4,default=Decimal('0.0000'))
    source=models.CharField(max_length=50)
    id_in_source=models.CharField(max_length=50)
    chromosome=models.CharField(max_length=50)

class star_allele(models.Model):
    id=models.AutoField(primary_key=True)
    star_id=models.CharField(max_length=250, default='NA') 
    star_annotation=models.CharField(max_length=50)
    drug=models.ForeignKey(drug, on_delete=models.CASCADE, default="DRUG1")
    allele=models.CharField(max_length=50)
    gene=models.ForeignKey(pharmacogenes, on_delete=models.CASCADE,default="PHARGENE19")
    phenotype=models.CharField(max_length=50)
    reference=models.ForeignKey(study, on_delete=models.CASCADE, default="REF1")
    p_value=models.CharField(max_length=10)
    #p_value=models.DecimalField(max_digits=10,decimal_places=4,default=Decimal('0.0000'))
    source=models.CharField(max_length=50)
    id_in_source=models.CharField(max_length=50)
    chromosome=models.CharField(max_length=50)

class snp_ethnicity_country(models.Model):
    id=models.CharField(max_length=250, primary_key=True)
    snp=models.CharField(max_length=50)
    #snp=models.ForeignKey(snp, on_delete=models.CASCADE)
    region=models.CharField(max_length=50)
    country_of_participants=models.CharField(max_length=50)
  
class star_allele_ethnicity_country(models.Model):
    id=models.CharField(max_length=250, primary_key=True)
    star_allele=models.CharField(max_length=50)
    #star_allele=models.ForeignKey(star_allele, on_delete=models.CASCADE)
    region=models.CharField(max_length=50)
    country_of_participants=models.CharField(max_length=50)