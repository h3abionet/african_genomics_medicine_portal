from django.contrib import admin

# Register your models here.
from .models import pharmacogenes, drug, snp, star_allele, study, Variantagmp, Drugagmp, Geneagmp, VariantStudyagmp, Studyagmp, Phenotypeagmp

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

@admin.register(pharmacogenes)
class PharmacogenesAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "chromosome_patch",
        "gene_name",
        "uniprot_id",
    )

@admin.register(drug)
class DrugsAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "drug_name",
        "drug_bank_id",
        "state",
        "iupac_name"
    )

@admin.register(snp)
class SNPAdmin(admin.ModelAdmin):
    list_display = (
        "id",
        "snp_id",
        "rs_id",
    )

@admin.register(star_allele)
class star_alleleAdmin(admin.ModelAdmin):
    list_display = (
        "star_id",
        "star_annotation",
        )

admin.site.register(study)
# admin.site.register(CountryData)
