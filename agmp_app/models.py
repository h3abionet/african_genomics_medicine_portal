from django.db import models
from decimal import Decimal
import geocoder
from django.urls import reverse

#====New Models=======#
from django.db import models


#Drug ids
def increment_drug_id():
    last_drug_id = Drugagmp.objects.all().order_by('id').last()
    if not last_drug_id:
        return 'DRUG001'
    drug_id = last_drug_id.drug_id
    width = 3
    drug_id_int = int(drug_id.split('DRUG')[-1])
    new_drug_id_int = drug_id_int + 1
    formatted = (width - len(str(new_drug_id_int))) * \
        "0" + str(new_drug_id_int)
    new_drug_id = 'DRUG' + str(formatted)
    return new_drug_id

######### New Models #############
class Drugagmp(models.Model):
    # drug_id = models.CharField(max_length=50, null=True, blank=True)
    drug_bank_id = models.CharField(max_length=500, null=True, blank=True)
    drug_name = models.CharField(max_length=500, null=True, blank=True)
    indication = models.TextField(max_length=500, null=True, blank=True)
    iupac_name_seq = models.CharField(max_length=500, null=True, blank=True)
    state = models.CharField(max_length=500, null=True, blank=True)
    # will be autogenerated on save
    drug_id = models.CharField(
        max_length=255, default=increment_drug_id, null=True, blank=True)
    class Meta:
        verbose_name_plural = "* Drugs"
        
    def __str__(self):
        return f"{self.drug_id}"

class Geneagmp(models.Model):
     # will be autogenerated on save
    gene_id = models.CharField(max_length=500, null=True, blank=True)
    # gene_id =models.UUIDField(primary_key=True, default= uuid.uuid4,editable=False)
    chromosome = models.CharField(max_length=500, null=True, blank=True)
    function = models.TextField(max_length=500, null=True, blank=True)
    gene_name= models.CharField(max_length=500, null=True, blank=True)
    uniprot_ac= models.CharField(max_length=500, null=True, blank=True)
 
    class Meta:
        verbose_name_plural = "* Gene"

    def __str__(self):
        return f"{self.gene_id}"

class Studyagmp(models.Model):
    data_ac = models.CharField(max_length=500, null=True, blank=True)
    publication_id = models.CharField(max_length=500, null=True, blank=True)
    publication_type = models.CharField(max_length=500, null=True, blank=True)
    publication_year = models.CharField(max_length=50, null=True, blank=True)
    study_type = models.CharField(max_length=500, null=True, blank=True)
    title = models.TextField(max_length=500, null=True, blank=True)
    class Meta:
        verbose_name_plural = "* Studies"

class Phenotypeagmp(models.Model): # will be the diseases
    name = models.TextField(max_length=500, null=True, blank=True)
    class Meta:
        verbose_name_plural = "* Phenotype"
   
class Variantagmp(models.Model):
    geneagmp = models.ForeignKey(Geneagmp, on_delete=models.CASCADE, default="GENE",null=True, blank=True)
    allele = models.CharField(max_length=500, null=True, blank=True)
    drugagmp = models.ForeignKey(Drugagmp, on_delete=models.CASCADE, related_name="drugs", default="DRUG",null=True, blank=True)
    source_db = models.CharField(max_length=500, null=True, blank=True)
    studyagmp = models.ForeignKey(Studyagmp, on_delete=models.CASCADE, related_name="studys",null=True, blank=True)
    phenotypeagmp = models.ForeignKey(Phenotypeagmp, on_delete=models.CASCADE,null=True, blank=True)
    # extra models
    id_in_source_db = models.CharField(max_length=500, null=True, blank=True)
    rs_id_star_annotation = models.CharField(max_length=500, null=True, blank=True) #which column is this in the csv file?
    variant_type = models.CharField(max_length=500, null=True, blank=True)
    rs_id = models.CharField(max_length=500, null=True, blank=True)
    class Meta:
        verbose_name_plural = "* Variant"

class VariantStudyagmp(models.Model):
    variantagmp = models.ForeignKey(Variantagmp, on_delete=models.CASCADE,null=True, blank=True)
    studyagmp = models.ForeignKey(Studyagmp, on_delete=models.CASCADE,null=True, blank=True)
    #country participant
    country_participant = models.CharField(max_length=500, null=True, blank=True)
    latitude = models.CharField(max_length=500, null=True, blank=True)
    longitude = models.CharField(max_length=500, null=True, blank=True)
     #country participant
    country_participant_01 = models.CharField(max_length=500, null=True, blank=True)
    latitude_01 = models.CharField(max_length=500, null=True, blank=True)
    longitude_01 = models.CharField(max_length=500, null=True, blank=True)
     #country participant
    country_participant_02 = models.CharField(max_length=500, null=True, blank=True)
    latitude_02 = models.CharField(max_length=500, null=True, blank=True)
    longitude_02 = models.CharField(max_length=500, null=True, blank=True)
     #country participant
    #country participant
    country_participant_03 = models.CharField(max_length=500, null=True, blank=True)
    latitude_03 = models.CharField(max_length=500, null=True, blank=True)
    longitude_03 = models.CharField(max_length=500, null=True, blank=True)
    #country participant
    country_participant_04 = models.CharField(max_length=500, null=True, blank=True)
    latitude_04 = models.CharField(max_length=500, null=True, blank=True)
    longitude_04 = models.CharField(max_length=500, null=True, blank=True)
     #country participant
    country_participant_05 = models.CharField(max_length=500, null=True, blank=True)
    latitude_05 = models.CharField(max_length=500, null=True, blank=True)
    longitude_05 = models.CharField(max_length=500, null=True, blank=True)
     #country participant
    country_participant_06 = models.CharField(max_length=500, null=True, blank=True)
    latitude_06 = models.CharField(max_length=500, null=True, blank=True)
    longitude_06 = models.CharField(max_length=500, null=True, blank=True)
     #country participant
    country_participant_07 = models.CharField(max_length=500, null=True, blank=True)
    latitude_07 = models.CharField(max_length=500, null=True, blank=True)
    longitude_07 = models.CharField(max_length=500, null=True, blank=True)
     #country participant

    country_participant_08 = models.CharField(max_length=500, null=True, blank=True)
    latitude_08 = models.CharField(max_length=500, null=True, blank=True)
    longitude_08 = models.CharField(max_length=500, null=True, blank=True)
     #country participant

    country_participant_09 = models.CharField(max_length=500, null=True, blank=True)
    latitude_09 = models.CharField(max_length=500, null=True, blank=True)
    longitude_09 = models.CharField(max_length=500, null=True, blank=True)
     #country participant

    country_participant_010 = models.CharField(max_length=500, null=True, blank=True)
    latitude_10 = models.CharField(max_length=500, null=True, blank=True)
    longitude_10 = models.CharField(max_length=500, null=True, blank=True)
    #country participant

    country_participant_011 = models.CharField(max_length=500, null=True, blank=True)
    latitude_11 = models.CharField(max_length=500, null=True, blank=True)
    longitude_11 = models.CharField(max_length=500, null=True, blank=True)

    ethnicity = models.CharField(max_length=500, null=True, blank=True)
    geographical_regions = models.CharField(max_length=500, null=True, blank=True)
    notes = models.TextField(max_length=500, null=True, blank=True)
    p_value = models.CharField(max_length=500, null=True, blank=True)


    class Meta:
        verbose_name_plural = "* Variant Studies"

#====New Models=======#

