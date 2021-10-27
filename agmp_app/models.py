from django.db import models
from decimal import Decimal


class Gene(models.Model):
    gene_id = models.CharField(primary_key=True, max_length=50)
    gene_name = models.CharField(max_length=50, default="NA")
    uniprot_ac = models.CharField(max_length=50, null=True)
    function = models.TextField(default="NA", max_length=2500, null=True)
    chromosome = models.CharField(default="NA", max_length=50)

class Variant(models.Model):
    variant_id = models.CharField(max_length=50)
    rs_id_star_annotation = models.CharField(max_length=50)
    variant_type = models.CharField(max_length=50)
    allele = models.CharField(max_length=50)
    clinical_significance = models.CharField(
        max_length=50, null=True, blank=True)
    clinvar_variation_id = models.CharField(
        max_length=50, null=True, blank=True)
    source_db = models.CharField(max_length=50)
    id_in_source_db = models.CharField(max_length=50)
    gene = models.ForeignKey(Gene, on_delete=models.CASCADE, null=True)
    drugs = models.ManyToManyField("Drug")
    #phenotypes = models.ManyToManyField("Phenotype")
    #studies = models.ManyToManyField("Study")

class Study(models.Model):
    study_id = models.CharField(primary_key=True, max_length=50)
    publication_id = models.CharField(max_length=50, default="NA")
    publication_type = models.CharField(max_length=50, null=True)
    publication_year = models.CharField(max_length=50, null=True, default="NA")
    title = models.CharField(max_length=250, default="NA")
    study_type = models.CharField(max_length=50, default="NA")
    data_ac = models.CharField(max_length=50, default="NA")
    variants = models.ManyToManyField("Variant", through='Variant_Study')

class Variant_Study(models.Model):
    variant = models.ForeignKey("Variant", on_delete=models.CASCADE)
    study = models.ForeignKey("Study", on_delete=models.CASCADE)
    p_value = models.FloatField(null=True)
    p_value_is_exact = models.BooleanField(default=True)
    country_of_participants = models.CharField(
        max_length=50, null=True, default="NA")
    geographical_regions = models.CharField(
        max_length=50, null=True, default="NA")
    ethnicity = models.CharField(max_length=50, null=True, default="NA")
    notes = models.TextField(max_length=2500, null=True, default="NA")


class Phenotype(models.Model):
    phenotype_id = models.CharField(max_length=250, primary_key=True)
    name = models.CharField(max_length=250)
    variants = models.ManyToManyField("Variant")

class Drug(models.Model):
    drug_id = models.CharField(max_length=250, primary_key=True)
    drug_bank_id = models.CharField(max_length=50, null=True)
    drug_name = models.CharField(max_length=250)
    state = models.CharField(max_length=250, null=True)
    indication = models.TextField()
    iupac_name_or_sequence = models.TextField()
    

# class Index(models.Model):
#     id=models.AutoField(primary_key=True)
#     recname=models.CharField(max_length=250)
#     keywords=models.CharField(default="NA",max_length=250)

# class drug(models.Model):
#     id=models.CharField(max_length=50, primary_key=True, default="DRUG0")
#     drug_name=models.CharField(max_length=250)
#     drug_bank_id=models.CharField(max_length=50, null=True)
#     state=models.CharField(max_length=250, null=True)
#     indication=models.TextField()
#     iupac_name=models.TextField()

# class disease(models.Model):
#     id=models.CharField(max_length=50, primary_key=True, default="DIS0")
#     disease_name=models.CharField(max_length=250)

# class study(models.Model):
#     id=models.CharField(max_length=50, primary_key=True)
#     reference_id=models.CharField(max_length=50)
#     type=models.CharField(max_length=250)
#     year=models.CharField(max_length=10, default="NA")
#     title=models.CharField(max_length=250)

# class pharmacogenes(models.Model):
#     id=models.CharField(max_length=50, default="GENE0", primary_key=True)
#     chromosome_patch=models.CharField(default="NA",max_length=50)
#     gene_name=models.CharField(max_length=50, default="NA")
#     uniprot_id=models.CharField(max_length=50, null=True)
#     function=models.TextField(default="NA",max_length=250, null=True)

# class snp(models.Model):
#     id=models.AutoField(primary_key=True)
#     varient_id=models.CharField(max_length=50, default='NA')
#     rs_id=models.CharField(max_length=50, default="RS0")
#     gene=models.ForeignKey(pharmacogenes, on_delete=models.CASCADE, default="GENE0")
#     drug=models.ForeignKey(drug, on_delete=models.CASCADE, default="DRUG0")
#     disease=models.ForeignKey(disease, on_delete=models.CASCADE, default="DIS0")
#     allele=models.CharField(max_length=50)
#     association_with=models.TextField(default="NA")
#     reference=models.ForeignKey(study, on_delete=models.CASCADE)
#     p_value=models.CharField(max_length=10, null=True)
#     source=models.CharField(max_length=50, null=True)
#     id_in_source=models.CharField(max_length=50, null=True)
#     region=models.CharField(max_length=50, default="Undetermined")
#     country_of_participants=models.CharField(max_length=50, null=True)
#     latitude = models.DecimalField(max_digits=10,decimal_places=7,default=Decimal('0.0000000'))
#     longitude = models.DecimalField(max_digits=10,decimal_places=7,default=Decimal('0.0000000'))

# class star_allele(models.Model):
#     id=models.AutoField(primary_key=True)
#     star_id=models.CharField(max_length=50, default='NA')
#     star_annotation=models.CharField(max_length=50)
#     gene=models.ForeignKey(pharmacogenes, on_delete=models.CASCADE, default="GENE0")
#     drug=models.ForeignKey(drug, on_delete=models.CASCADE, default="DRUG0")
#     allele=models.CharField(max_length=50)
#     phenotype=models.TextField(default="NA")
#     reference=models.ForeignKey(study, on_delete=models.CASCADE, null=True)
#     p_value=models.CharField(max_length=20, null=True)
#     source=models.CharField(max_length=50, null=True)
#     id_in_source=models.CharField(max_length=50, null=True)
#     region=models.CharField(max_length=50, default="Undetermined")
#     country_of_participants=models.CharField(max_length=50, null=True)
#     latitude = models.DecimalField(max_digits=10,decimal_places=7,default=Decimal('0.0000000'))
#     longitude = models.DecimalField(max_digits=10,decimal_places=7,default=Decimal('0.0000000'))
