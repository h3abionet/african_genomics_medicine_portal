from django.db import models
from decimal import Decimal
import geocoder


class Index(models.Model):
    id = models.AutoField(primary_key=True)
    recname = models.CharField(max_length=250)
    keywords = models.CharField(default="NA", max_length=250)


class drug(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default="DRUG0")
    drug_name = models.CharField(max_length=250)
    drug_bank_id = models.CharField(max_length=50, null=True)
    state = models.CharField(max_length=250, null=True)
    indication = models.TextField()
    iupac_name = models.TextField()
    
    def __str__(self):
        return f"{self.drug_name}"


class disease(models.Model):
    id = models.CharField(max_length=50, primary_key=True, default="DIS0")
    disease_name = models.CharField(max_length=250)
    
    def __str__(self):
        return f"{self.disease_name}"


class study(models.Model):
    id = models.CharField(max_length=50, primary_key=True)
    reference_id = models.CharField(max_length=50)
    type = models.CharField(max_length=250)
    year = models.CharField(max_length=10, default="NA")
    title = models.CharField(max_length=250)
    
    def __str__(self):
        return f"{self.title}"
    
    class Meta:
        verbose_name_plural = "Studies"


class pharmacogenes(models.Model):
    id = models.CharField(max_length=50, default="GENE0", primary_key=True)
    chromosome_patch = models.CharField(default="NA", max_length=50)
    gene_name = models.CharField(max_length=50, default="NA")
    uniprot_id = models.CharField(max_length=50, null=True)
    function = models.TextField(default="NA", max_length=250, null=True)
    
    def __str__(self):
        return f"{self.uniprot_id}"
    
    class Meta:
        verbose_name_plural = "Pharmacogenes"


class snp(models.Model):
    id = models.AutoField(primary_key=True)
    snp_id = models.CharField(max_length=50, default='NA')
    rs_id = models.CharField(max_length=50, default="RS0")
    gene = models.ForeignKey(
        pharmacogenes, on_delete=models.CASCADE, default="GENE0")
    drug = models.ForeignKey(drug, on_delete=models.CASCADE, default="DRUG0")
    disease = models.ForeignKey(
        disease, on_delete=models.CASCADE, default="DIS0")
    allele = models.CharField(max_length=50)
    association_with = models.TextField(default="NA")
    reference = models.ForeignKey(study, on_delete=models.CASCADE)
    p_value = models.CharField(max_length=10, null=True)
    source = models.CharField(max_length=50, null=True)
    id_in_source = models.CharField(max_length=50, null=True)
    region = models.CharField(max_length=50, default="Undetermined")
    country_of_participants = models.CharField(max_length=50, null=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, default=Decimal('0.0000000'))
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, default=Decimal('0.0000000'))

    def save(self, *args, **kwargs):
        self.latitude = geocoder.osm(self.country_of_participants).lat
        self.longitude = geocoder.osm(self.country_of_participants).lng
        return super().save(*args, **kwargs)
    
    def __str__(self):
        return f"{self.snp_id}"
    
    class Meta:
        verbose_name_plural = "SNPs"


class star_allele(models.Model):
    star_id = models.CharField(max_length=50, default='NA')
    star_annotation = models.CharField(max_length=50)
    gene = models.ForeignKey(
        pharmacogenes, on_delete=models.CASCADE, default="GENE0")
    drug = models.ForeignKey(drug, on_delete=models.CASCADE, default="DRUG0")
    allele = models.CharField(max_length=50)
    phenotype = models.TextField(default="NA")
    reference = models.ForeignKey(study, on_delete=models.CASCADE, null=True)
    p_value = models.CharField(max_length=20, null=True)
    source = models.CharField(max_length=50, null=True)
    id_in_source = models.CharField(max_length=50, null=True)
    region = models.CharField(max_length=50, default="Undetermined")
    country_of_participants = models.CharField(max_length=50, null=True)
    latitude = models.DecimalField(
        max_digits=10, decimal_places=7, default=Decimal('0.0000000'))
    longitude = models.DecimalField(
        max_digits=10, decimal_places=7, default=Decimal('0.0000000'))
    
    def __str__(self):
        return f"{self.star_id}"
    
    class Meta:
        verbose_name_plural = "Star alleles"


class CountryData(models.Model):
    country = models.CharField(max_length=100)
    population = models.IntegerField()

    class Meta:
        verbose_name_plural = 'Country Population Data'

    def __str__(self):
        return f'{self.country} - {self.population}'
