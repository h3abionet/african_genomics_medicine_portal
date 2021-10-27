from django.contrib import admin

# Register your models here.
from .models import Gene, Drug, Variant, Study


class GeneAdmin(admin.ModelAdmin):
    list_display = ( 'gene_id','gene_name', 'uniprot_ac')

class VariantAdmin(admin.ModelAdmin):
    list_display = ( 'rs_id_star_annotation','variant_type', 'source_db')

class DrugAdmin(admin.ModelAdmin):
    list_display = ( 'drug_id','drug_bank_id', 'iupac_name_or_sequence')



admin.site.register(Gene, GeneAdmin)
admin.site.register(Variant, VariantAdmin)
admin.site.register(Drug, DrugAdmin)

# from .models import pharmacogenes, drug, snp, star_allele, study

# admin.site.register(pharmacogenes)
# admin.site.register(drug)
# admin.site.register(snp)
# admin.site.register(star_allele)
# admin.site.register(study)
