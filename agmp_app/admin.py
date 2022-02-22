from dataclasses import fields
from django.contrib import admin

# Register your models here.
from .models import pharmacogenes, drug, snp, star_allele, study, City, Country, CountryData

class CityAdmin(admin.ModelAdmin):
   list_display = ['id','name']

class CountryAdmin(admin.ModelAdmin):
   list_display = ['id','name']

admin.site.register(pharmacogenes)
admin.site.register(drug)
admin.site.register(snp)
admin.site.register(star_allele)
admin.site.register(study)
admin.site.register(Country)
admin.site.register(City)
admin.site.register(CountryData)