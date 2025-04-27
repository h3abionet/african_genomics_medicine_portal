from django.contrib import admin

# Register your models here.
from .models import Variantagmp, Drugagmp, Geneagmp, VariantStudyagmp, Studyagmp, Phenotypeagmp, ClinPhenData, DataBaseClinicalSig

class VariantagmpAdmin(admin.ModelAdmin):
    list_display = ['id','rs_id','source_db','id_in_source_db','variant_type','geneagmp',]
    search_fields =['rs_id','source_db','id_in_source_db','variant_type',]
    list_per_page = 500
    # pass
class DrugagmpAdmin(admin.ModelAdmin):
    list_display = ['id','drug_id','drug_name','drug_bank_id','indication','state']
    search_fields =['drug_id','drug_name','drug_bank_id','indication',]
    list_per_page = 500

class GeneagmpAdmin(admin.ModelAdmin):
    list_display = ['id', 'gene_id','gene_name','chromosome','function','uniprot_ac']
    search_fields =['gene_id','gene_name','chromosome','function',]
    list_per_page = 500
  

class VariantStudyagmpAdmin(admin.ModelAdmin):
    list_display = ['id','latitude_01','longitude_01','latitude_02','longitude_02','latitude_03','longitude_03','latitude_04','longitude_04','latitude_05','longitude_05','latitude_06','longitude_06','latitude_07','longitude_08','latitude_09','longitude_09','latitude_10','longitude_10','latitude_11','longitude_11','geographical_regions','mixed_population','ethnicity','notes','p_value']
    search_fields =['p_value','mixed_population','ethnicity','notes',]
    list_per_page = 500

class StudyagmpAdmin(admin.ModelAdmin):
    list_display = ['id','study_type','publication_id','publication_type','publication_year','title']
    list_per_page = 500
    search_fields =['title','publication_id','publication_type','publication_year',]

class PhenotypeagmpAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    search_fields =['name']
    list_per_page = 500
###Gen2phen new models ####
class ClinPhenDataAdmin(admin.ModelAdmin):
    list_display = ['phenotype_id', 'disease_class', 'hpo_class', 'who_class', 'curated_data', 'comorbidities', 'symptoms']
    search_fields = ['disease_class', 'hpo_class', 'who_class', 'curated_data', 'comorbidities', 'symptoms']
    list_per_page = 500

class DataBaseClinicalSigAdmin(admin.ModelAdmin):
    list_display = ['id', 'clin_sign', 'database_link', 'func_pred_toolname']
    search_fields = ['clin_sign', 'database_link', 'func_pred_toolname']
    list_per_page = 500

###### site.register ######
admin.site.register(Drugagmp, DrugagmpAdmin)
admin.site.register(Variantagmp, VariantagmpAdmin)
admin.site.register(Geneagmp, GeneagmpAdmin)
admin.site.register(VariantStudyagmp, VariantStudyagmpAdmin)
admin.site.register(Studyagmp, StudyagmpAdmin)
admin.site.register(Phenotypeagmp, PhenotypeagmpAdmin)
### new site register for gen2phen###
admin.site.register(ClinPhenData, ClinPhenDataAdmin)
admin.site.register(DataBaseClinicalSig, DataBaseClinicalSigAdmin)
admin.site.site_header = 'AGMP admin'
admin.site.site_title = 'AGMP admin'
admin.site.index_title = 'AGMP admin home'

