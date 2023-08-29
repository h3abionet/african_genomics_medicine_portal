from django.contrib import admin

# Register your models here.
from .models import Variantagmp, Drugagmp, Geneagmp, VariantStudyagmp, Studyagmp, Phenotypeagmp
###### New classes ######
class VariantagmpAdmin(admin.ModelAdmin):
    list_display = ['id']
    # pass
class DrugagmpAdmin(admin.ModelAdmin):
    list_display = ['id','drug_id']
    search_fields =['drug_id']

class GeneagmpAdmin(admin.ModelAdmin):
    list_display = ['id', 'gene_id']
    search_fields =['gene_id']
  

class VariantStudyagmpAdmin(admin.ModelAdmin):
    list_display = ['id']
    search_fields =['country_participant','notes']

class StudyagmpAdmin(admin.ModelAdmin):
    list_display = ['id']

class PhenotypeagmpAdmin(admin.ModelAdmin):
    list_display = ['id']

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

