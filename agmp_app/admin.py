from django.contrib import admin

# Register your models here.
from .models import Variantagmp, Drugagmp, Geneagmp, VariantStudyagmp, Studyagmp, Phenotypeagmp

class VariantagmpAdmin(admin.ModelAdmin):
    list_display = ['id','rs_id','source_db','id_in_source_db','variant_type','geneagmp',]
    search_fields =['rs_id']
    list_per_page = 500
    # pass
class DrugagmpAdmin(admin.ModelAdmin):
    list_display = ['id','drug_id','drug_name','drug_bank_id','indication','state']
    search_fields =['drug_id']
    list_per_page = 500

class GeneagmpAdmin(admin.ModelAdmin):
    list_display = ['id', 'gene_id','gene_name','chromosome','function','uniprot_ac']
    search_fields =['gene_id']
    list_per_page = 500
  

class VariantStudyagmpAdmin(admin.ModelAdmin):
    list_display = ['id','latitude_01','longitude_01','latitude_02','longitude_02','latitude_03','longitude_03','latitude_04','longitude_04','latitude_05','longitude_05','latitude_06','longitude_06','latitude_07','longitude_08','latitude_09','longitude_09','latitude_10','longitude_10','latitude_11','longitude_11','geographical_regions','mixed_population','ethnicity','notes','p_value']
    search_fields =['country_participant']
    list_per_page = 500

class StudyagmpAdmin(admin.ModelAdmin):
    list_display = ['id','study_type','publication_id','publication_type','publication_year','title']
    list_per_page = 500
    search_fields =['title']

class PhenotypeagmpAdmin(admin.ModelAdmin):
    list_display = ['id','name']
    search_fields =['name']
    list_per_page = 500

###### site.register ######
admin.site.register(Drugagmp, DrugagmpAdmin)
admin.site.register(Variantagmp, VariantagmpAdmin)
admin.site.register(Geneagmp, GeneagmpAdmin)
admin.site.register(VariantStudyagmp, VariantStudyagmpAdmin)
admin.site.register(Studyagmp, StudyagmpAdmin)
admin.site.register(Phenotypeagmp, PhenotypeagmpAdmin)

admin.site.site_header = 'AGMP admin'
admin.site.site_title = 'AGMP admin'
admin.site.index_title = 'AGMP admin home'

