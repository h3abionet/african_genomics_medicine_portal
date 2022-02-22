from django.contrib import admin

# Register your models here.
from .models import pharmacogenes, drug, snp, star_allele, study, CountryData

admin.site.register(pharmacogenes)
admin.site.register(drug)
admin.site.register(snp)
admin.site.register(star_allele)
admin.site.register(study)
admin.site.register(CountryData)