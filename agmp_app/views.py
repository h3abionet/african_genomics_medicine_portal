from urllib.parse import DefragResult
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import FileResponse

from django.core import serializers
from itertools import chain
from .forms import SearchForm,ModelSearchForm
import json
import folium
from folium.plugins import HeatMap
import math
import geocoder
from folium import plugins

from agmp_app.models import *
from django.db.models import Avg, Min, Max, Count, Q,F
import pandas as pd
from collections import Counter
from django_pandas.io import read_frame
from django.views.generic.detail import DetailView

from django.views.generic import ListView

from django.http import JsonResponse
from django.views.generic import TemplateView

from collections import defaultdict
import folium
import logging

import numpy as np
import logging

from django.db.models import Subquery, OuterRef

import os
import re

from django.conf import settings
import geopandas as gpd
from shapely.geometry import Point
from fuzzywuzzy import fuzz
from fuzzywuzzy import process
from django.http import Http404
 
 #heatmap-colors
COLORS = {
    "brick_red": "#8B4513",
    "darker_red": "#B22222",
    "lighter_red": "#CD5C5C",
    "orange_yellow": "#FFB266",
    "light_yellow": "#FFFF99",
} 
 #current search view
def search_view(request):
    form = ModelSearchForm(request.GET)
    model_selection = ""
    suggestion = None

    if form.is_valid():
        model_selection = form.cleaned_data['model_selection']
        search_query = form.cleaned_data['search_query']

        if model_selection == 'variantagmp':
            results = Variantagmp.objects.filter(rs_id__icontains=search_query).values('rs_id', 'geneagmp__gene_id', 'geneagmp__chromosome').distinct()
            if not results:
                all_variants = Variantagmp.objects.values_list('rs_id', flat=True)
                suggestion = process.extractOne(search_query, all_variants)

        elif model_selection == 'geneagmp':
            results = Geneagmp.objects.filter(gene_id__icontains=search_query).values('gene_id', 'chromosome').distinct()
            if not results:
                all_genes = Geneagmp.objects.values_list('gene_id', flat=True)
                suggestion = process.extractOne(search_query, all_genes)

        elif model_selection == 'drugagmp':
            results = Drugagmp.objects.filter(drug_name__icontains=search_query).values('drug_name', 'drug_id', 'drug_bank_id', 'state', 'indication', 'iupac_name_seq').distinct()
            if not results:
                all_drugs = Drugagmp.objects.values_list('drug_name', flat=True)
                suggestion = process.extractOne(search_query, all_drugs)

        elif model_selection == 'disease':
            results = Variantagmp.objects.select_related().exclude(source_db="PharmGKB").filter(phenotypeagmp__name__icontains=search_query).values("phenotypeagmp__name").distinct()
            if not results:
                all_diseases = Variantagmp.objects.exclude(source_db="PharmGKB").values_list('phenotypeagmp__name', flat=True).distinct()
                suggestion = process.extractOne(search_query, all_diseases)
    else:
        results = []

    return render(request, 'search_list_template.html', {
        'form': form,
        'results': results,
        'model_selection': model_selection,
        'suggestion': suggestion
    })

def search_all(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            search_option = form.cleaned_data['search_option']
            search_query = form.cleaned_data['search_query']
            
            if search_option == 'Variantagmp':
                results = Variantagmp.objects.filter(rs_id__icontains=search_query).values("rs_id","geneagmp__gene_id","geneagmp__chromosome","variant_type").distinct()
            elif search_option == 'Geneagmp':
                results = Geneagmp.objects.filter(gene_id__icontains=search_query)
            elif search_option == 'Drugagmp':
                results = Drugagmp.objects.filter(drug_name__contains=search_query).order_by('drug_name').distinct(F('drug_name').desc())
                #results = Drugagmp.objects.filter(drug_name__contains=search_query)
            elif search_option == 'Disease':
                #initial_query_results = Variantagmp.objects.select_related().exclude(source_db="PharmGKB").filter(phenotypeagmp__name__contains=search_query)
                #second_initial_query_results = Variantagmp.objects.select_related().exclude(source_db="PharmGKB").filter(phenotypeagmp__name__contains=search_query).filter(phenotypeagmp__isnull=False).values("phenotypeagmp__name").distinct()
                results = Variantagmp.objects.select_related().exclude(source_db="PharmGKB").filter(phenotypeagmp__name__icontains=search_query).values("phenotypeagmp__name").distinct()
                     
            return render(request, 'search_form.html', {'form': form, 'results': results, 'search_option':search_option})
    else:
        form = SearchForm()
        
    return render(request, 'search_form.html', {'form': form})


 #################### Variant Drug Details 1 ################################

class DrugagmpDetailView(DetailView):
    model = Drugagmp
    template_name = 'drugagmp_detail.html'  # Template to display the post details

class VariantStudyagmpListView(ListView):
    model = VariantStudyagmp
    template_name = 'variantstudyagmp_list.html'  # Template to display the comment list

    def get_queryset(self):
        drug_id = self.kwargs['pk']  # Get the post id from URL parameter
        return VariantStudyagmp.objects.filter(Variantagmp__drugagmp_icontains=drug_id)  # Filter comments by post id


  
 #################### Variant Drug Details ################################
  
 #################### PharmacoGene Associations exclude Gwas catalogue in the first queryset ################################
#03 Drug associations and Phenotype Associations
class PhamacogeneDrugAssoc(DetailView):
    model = VariantStudyagmp
    template_name = 'PhamacogeneDrugAssoc.html'
    pk_url_kwarg = 'gene_id'
    context_object_name = 'variantstudyagmp'


    def get_object(self):
        gene_id = self.kwargs.get(self.pk_url_kwarg)

        data = Geneagmp.objects.filter(gene_id=gene_id)
        # print(data) # for testing purposes
        return data
    
    def get_context_data(self, **kwargs):
        context = super(PhamacogeneDrugAssoc, self).get_context_data(**kwargs)
        gene_id = self.kwargs.get(self.pk_url_kwarg)

        #content to display
        context['geneagmp'] = Geneagmp.objects.filter(
            gene_id=gene_id)
        
        context["data"] = Geneagmp.objects.filter(gene_id = gene_id).first()
       
       #include PharmGKB and Exclude Gwas Catalogue & DisGeNET
        context['object_list'] = VariantStudyagmp.objects.filter(
    variantagmp__geneagmp__gene_id__iregex=r"(^|[^a-zA-Z0-9_]){0}([^a-zA-Z0-9_]|$)".format(
        re.escape(str(gene_id)).replace('\\ ', '\\s+')
    )
).exclude(
    variantagmp__source_db__in=["DisGeNET", "GWAS Catalog"])
        

        context['object_list_diseases'] = VariantStudyagmp.objects.filter(
    variantagmp__geneagmp__gene_id__iregex=r"(^|[^a-zA-Z0-9_]){0}([^a-zA-Z0-9_]|$)".format(re.escape(str(gene_id))),
    variantagmp__source_db__in=["DisGeNet", "GWAS Catalog"]
).exclude(
    variantagmp__source_db="PharmGKB"
)
        
        return context

 #################### Gene Drug Associations ################################


 #################### Var Drug Associations exclude gwas catalogue ################################
class VarDrugAssocDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'VarDrugAssocDetail.html'
    pk_url_kwarg = 'rs_id'
    context_object_name = 'variantstudyagmp'

    def get_object(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)


        data = Variantagmp.objects.filter(rs_id=rs_id)
        # print(data) # for testing purposes
        return data
    
    def get_context_data(self, **kwargs):
        context = super(VarDrugAssocDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
          
        context['gene_id_display'] = Variantagmp.objects.values("geneagmp__gene_id").filter(rs_id=rs_id).first()
        context['chromosome_display'] = Variantagmp.objects.values("geneagmp__chromosome").filter(rs_id=rs_id).first()
        context['rs_id_display'] = Variantagmp.objects.values("rs_id").filter(rs_id=rs_id).first()
  

        #back up query
        context['object_list'] = VariantStudyagmp.objects.filter(
            variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id))).exclude(variantagmp__source_db="DisGeNET").exclude(variantagmp__source_db="GWAS Catalog")
        


        return context

 #################### Variant Disease Associations ################################
# 02 
class VariantDiseaseAssocDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'VariantDiseaseAssocDetail.html'
    pk_url_kwarg = 'rs_id'

    def get_object(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)

        data = Variantagmp.objects.filter(rs_id=rs_id)
        # print(data) # for testing purposes
        return data
    
    def get_context_data(self, **kwargs):
        context = super(VariantDiseaseAssocDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
     
        context['rs_id_display'] = (Variantagmp.objects.values("rs_id").filter(rs_id=rs_id))[0]

        context['gene_name_display'] = Variantagmp.objects.values("geneagmp__gene_id").filter(rs_id=rs_id).first()

        context['chromosome_display'] = Variantagmp.objects.values("geneagmp__chromosome").filter(rs_id=rs_id).first()

        context['object_list'] = VariantStudyagmp.objects.filter(
    variantagmp__rs_id__iregex=r"(^|[^a-zA-Z0-9_]){0}([^a-zA-Z0-9_]|$)".format(re.escape(str(rs_id))),
    variantagmp__source_db__iregex=r"^(DisGeNet|GWAS Catalog)$"
).exclude(variantagmp__source_db="PharmGKB")


        return context
    

  #################### DRUG searchs for Variant drug Associations ################################
#01
class VariantDrugAssociationDetailView(DetailView):
    model = Variantagmp
    pk_url_kwarg = 'rs_id'
    
    def get_template_names(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        if rs_id and rs_id.startswith("DB"):
            return ['VariantDrugAssociation.html']
        else:
            return ['VarDrugAssocDetail.html']
    
    def get_object(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        # If the ID starts with "DB", look up by drug ID instead
        if rs_id and rs_id.startswith("DB"):
            # Find a variant associated with this drug
            drug = get_object_or_404(Drugagmp, drug_bank_id=rs_id)
            variant = Variantagmp.objects.filter(drugagmp=drug).first()
            if variant:
                return variant
            else:
                # Still return something even if no variant is found
                # This allows the view to continue and show drug info
                return Variantagmp(drugagmp=drug)
        else:
            # For non-DB IDs - Always get the first matching variant when multiple exist
            try:
                # First try with a direct filter and first()
                variants = Variantagmp.objects.filter(rs_id=rs_id)
                if variants.exists():
                    return variants.first() # Return the first match
                else:
                    raise Http404(f"No variant found with rs_id: {rs_id}")
            except Variantagmp.DoesNotExist:
                raise Http404(f"No variant found with rs_id: {rs_id}")
                
    def get_context_data(self, **kwargs):
        context = super(VariantDrugAssociationDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        # If this is a drug ID, add drug data directly to context
        if rs_id and rs_id.startswith("DB"):
            drug = get_object_or_404(Drugagmp, drug_bank_id=rs_id)
            context['data'] = drug
            # Get all variant studies related to this drug
            variant_studies = VariantStudyagmp.objects.filter(
                variantagmp__drugagmp=drug
            ).select_related(
                'variantagmp',
                'studyagmp',
                'variantagmp__drugagmp',
                'variantagmp__geneagmp'
            )
            context['object_list'] = variant_studies
            # If we need an rs_id for other parts of the template, get it from the first variant
            variant = Variantagmp.objects.filter(drugagmp=drug).first()
            if variant:
                rs_id = variant.rs_id
            else:
                rs_id = None
        else:
            # If it's a variant ID, get associated drug info
            variant = self.object
            if variant and hasattr(variant, 'drugagmp') and variant.drugagmp:
                context['data'] = variant.drugagmp
                # Get all variant studies for this variant
                context['object_list'] = VariantStudyagmp.objects.filter(
                    variantagmp__rs_id=variant.rs_id
                ).select_related(
                    'variantagmp',
                    'studyagmp',
                    'variantagmp__drugagmp',
                    'variantagmp__geneagmp'
                )
        
        # Get the variant object for display in the template
        variant = self.object
        # Add variant info to context
        context['rs_id_display'] = variant
        # Get gene information for this variant
        if variant and hasattr(variant, 'geneagmp') and variant.geneagmp:
            context['gene_id_display'] = {
                'geneagmp__gene_id': variant.geneagmp.gene_id
            }
            context['chromosome_display'] = {
                'geneagmp__chromosome': variant.geneagmp.chromosome
            }
        return context

  #################### Variant Var Drug Associations ################################
class VvarDrugAssocDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'VarDrugAssocDetail.html'
    pk_url_kwarg = 'rs_id'

    def get_object(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)

        data = Variantagmp.objects.filter(rs_id=rs_id)
        # print(data) # for testing purposes
        return data
    
    def get_context_data(self, **kwargs):
        context = super(VvarDrugAssocDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
     
        context['variantagmp'] = Variantagmp.objects.filter(
            rs_id=rs_id)
        #content to display
        variant = Variantagmp.objects.filter(rs_id=rs_id)

        # context['object_list_01'] = Geneagmp.objects.filter(gene_id__iregex=r"\b{0}\b".format(str(rs_id)))
       
        #back up query
        context['object_list'] = VariantStudyagmp.objects.filter(
            variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id))) 
        
        # context['object_list'] = Variantagmp.objects.filter(geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id)))

        return context

 #################### Search Diseases ################################

# Display Phamacogenes and Disease associations
#04
class DiseaseVariantDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'DiseaseVariantDetailView.html'
    pk_url_kwarg = 'phenotypeagmp__name'


    def get_object(self):
        phenotypeagmp__name = self.kwargs.get(self.pk_url_kwarg)
    

        # data = Variantagmp.objects.get(rs_id=rs_id)
        # return data

    
    def get_context_data(self, **kwargs):
        context = super(DiseaseVariantDetailView, self).get_context_data(**kwargs)
        phenotypeagmp__name = self.kwargs.get(self.pk_url_kwarg)

        context['data'] = Variantagmp.objects.filter(
            phenotypeagmp__name=phenotypeagmp__name).values("phenotypeagmp__name").distinct()[0]
       
       
        context['object_list1'] = VariantStudyagmp.objects.select_related().filter(
    variantagmp__phenotypeagmp__name__iregex=r"\\y{0}\\y".format(str(phenotypeagmp__name))
).exclude(variantagmp__source_db="PharmGKB")
       
        context['object_list'] = VariantStudyagmp.objects.select_related().filter(
            variantagmp__phenotypeagmp__name__iexact=phenotypeagmp__name).exclude(variantagmp__source_db="PharmGKB")
       

        #context['object_list_diseases'] = VariantStudyagmp.objects.select_related().filter(variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id))).exclude(variantagmp__source_db="PharmGKB")
        
        
        return context
       
  #################### Variant Var Drug Associations ################################
class VarDisAssocDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'VarDissAssocDetail.html'
    pk_url_kwarg = 'rs_id'

    def get_object(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)

        data = Variantagmp.objects.filter(rs_id=rs_id)
     
        return data
    
    def get_context_data(self, **kwargs):
        context = super(VarDisAssocDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
     
        context['variantagmp'] = Variantagmp.objects.filter(
            rs_id=rs_id)
        #content to display
        variant = Variantagmp.objects.filter(rs_id=rs_id)

        # context['object_list_01'] = Geneagmp.objects.filter(gene_id__iregex=r"\b{0}\b".format(str(rs_id)))
       
        #back up query
        context['object_list'] = VariantStudyagmp.objects.filter(
            variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id))).exclude(variantagmp__source_db="PharmGKB")
        
        
        # context['object_list'] = Variantagmp.objects.filter(geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id)))

        return context

# Display Phamacogenes and Disease associations
class PharmacoDrugDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'PharmacoDrugDetailView.html'
    pk_url_kwarg = 'gene_id'
    

    def get_object(self):
        gene_id = self.kwargs.get(self.pk_url_kwarg)

        data = Geneagmp.objects.filter(gene_id=gene_id)
        return data
    
    def get_context_data(self, **kwargs):
        context = super(PharmacoDrugDetailView, self).get_context_data(**kwargs)
        gene_id = self.kwargs.get(self.pk_url_kwarg)

        context['geneagmp'] = Geneagmp.objects.filter(
            gene_id=gene_id).first()
        
        context['object_list'] = VariantStudyagmp.objects.filter(
            variantagmp__geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id))) 
        

        context['object_list_diseases_old']=VariantStudyagmp.objects.select_related().filter(variantagmp__geneagmp__gene_id__icontains=gene_id)

        #context['object_list_diseases'] = Variantagmp.objects.select_related().exclude(source_db="PharmGKB").filter(geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id)))

        context['object_list_diseases'] = VariantStudyagmp.objects.select_related().filter(variantagmp__geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id))).exclude(variantagmp__source_db="PharmGKB")
        
        
        return context


 #################### Variant Drug Details ################################

class DrugDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'drug_detail.html'
    pk_url_kwarg = 'drug_id'

    def get_object(self):
        drug_id = self.kwargs.get(self.pk_url_kwarg)

        data = Drugagmp.objects.filter(drug_id=drug_id)
       
        return data
    
    def get_context_data(self, **kwargs):
        context = super(DrugDetailView, self).get_context_data(**kwargs)
        drug_id = self.kwargs.get(self.pk_url_kwarg)
        context['drugagmp'] = Drugagmp.objects.filter(
            drug_id=drug_id).first()
        drug = Drugagmp.objects.filter(drug_id=drug_id).first()

        context['object_list'] = VariantStudyagmp.objects.filter(
            variantagmp__drugagmp__drug_id__iregex=r"\b{0}\b".format(str(drug_id)))
        

        context['drugagmp'] = Drugagmp.objects.filter(
           drug_id=drug.id).first()
        return context
def about(request):
    return render(request, 'about.html')

def get_map_data(request, map_type):
    """
    AJAX endpoint for getting map data based on study type filter
    """
    study_type = request.GET.get('study_type', 'All')
    
    def get_filtered_studies(study_type):
        studies = VariantStudyagmp.objects.all()
        if study_type and study_type != 'All':
            studies = studies.filter(studyagmp__study_type=study_type)
        return studies

    def get_location_data(lat_field, lon_field, queryset):
        return queryset.exclude(
            Q(**{f'{lon_field}__isnull': True}) | Q(**{f'{lon_field}__exact': ''}) |
            Q(**{f'{lat_field}__isnull': True}) | Q(**{f'{lat_field}__exact': ''})
        ).values('studyagmp__publication_id', lat_field, lon_field).annotate(
            latitude=F(lat_field),
            longitude=F(lon_field)
        ).values('latitude', 'longitude')

    location_fields = [
        ('latitude_01', 'longitude_01'), ('latitude_02', 'longitude_02'),
        ('latitude_03', 'longitude_03'), ('latitude_04', 'longitude_04'),
        ('latitude_05', 'longitude_05'), ('latitude_06', 'longitude_06'),
        ('latitude_07', 'longitude_07'), ('latitude_08', 'longitude_08'),
        ('latitude_09', 'longitude_09'), ('latitude_10', 'longitude_10'),
        ('latitude_11', 'longitude_11')
    ]

    # Get filtered studies and locations
    filtered_studies = get_filtered_studies(study_type)
    locations = [get_location_data(lat, lon, filtered_studies) for lat, lon in location_fields]
    flattened_locations = [item for sublist in locations for item in sublist]

    # Process coordinates
    count_per_coordinates = defaultdict(int)
    for record in flattened_locations:
        coordinates = (record["latitude"], record["longitude"])
        count_per_coordinates[coordinates] += 1

    if map_type == 'marker':
        # Create marker map
        m = folium.Map(location=[-4.0335, 21.7501], zoom_start=3)
        for coordinates, value in count_per_coordinates.items():
            try:
                clean_latitude = float(coordinates[0])
                clean_longitude = float(coordinates[1])
                popup_text = f"Publications: {value}"
                popup = folium.Popup(popup_text, parse_html=True)
                folium.Marker([clean_latitude, clean_longitude], popup=popup).add_to(m)
            except ValueError:
                logging.warning(f"Skipping invalid coordinates: {coordinates}")

        return JsonResponse({'map_html': m._repr_html_()})

    elif map_type == 'heatmap':
        # Create choropleth map
        m2 = folium.Map(location=[1.2921, 36.8219], zoom_start=3)
        geojson_path = os.path.join(settings.BASE_DIR, 'agmp_app/static/maps/countries.geo.json')
        gdf = gpd.read_file(geojson_path)

        publications_per_country = defaultdict(int)
        for (lat, lon), value in count_per_coordinates.items():
            try:
                point = Point(float(lon), float(lat))
                for _, row in gdf.iterrows():
                    if row['geometry'].contains(point):
                        publications_per_country[row['name']] += value
                        break
            except (ValueError, TypeError):
                logging.warning(f"Invalid coordinates: lat={lat}, lon={lon}")
                continue

        def get_color(value):
            if value > 1000:
                return "#8B0000" 
            elif value > 100:
                return "#CD5C5C"
            elif value > 50:
                return "#DAA520"
            elif value > 10:
                return "#F0E68C"
            else:
                return "#FFFFE0"

        for _, row in gdf.iterrows():
            country_name = row['name']
            publication_count = publications_per_country[country_name]
            color = get_color(publication_count)
            
            tooltip_text = f"{country_name}: {publication_count:,} publications"
            
            folium.GeoJson(
                row['geometry'],
                style_function=lambda feature, color=color: {
                    "fillColor": color,
                    "color": "black",
                    "weight": 1,
                    "fillOpacity": 0.7,
                },
                tooltip=folium.Tooltip(
                    tooltip_text,
                    style="""
                        background-color: white;
                        color: black;
                        font-family: arial;
                        font-size: 12px;
                        padding: 10px;
                        border-radius: 3px;
                        box-shadow: 3px 3px 3px rgba(0,0,0,0.2);
                    """
                )
            ).add_to(m2)

        # Add legends
        custom_legend_html = '''
         <div style="position: fixed; bottom: 50px; left: 50px; width: 200px; height: 200px; 
         background-color: white; border:2px solid grey; z-index:9999; font-size:14px;
         border-radius: 5px; box-shadow: 3px 3px 3px rgba(0,0,0,0.2);">
         &nbsp; <b>Publications</b> <br>
         &nbsp; > 1000 &nbsp; <i style="background: #8B0000; width:20px; height:20px; float:right; margin-top:3px;"></i><br>
         &nbsp; 100 - 1000 &nbsp; <i style="background: #CD5C5C; width:20px; height:20px; float:right; margin-top:3px;"></i><br>
         &nbsp; 50 - 100 &nbsp; <i style="background: #DAA520; width:20px; height:20px; float:right; margin-top:3px;"></i><br>
         &nbsp; 10 - 50 &nbsp; <i style="background:  #F0E68C; width:20px; height:20px; float:right; margin-top:3px;"></i><br>
         &nbsp; 0 - 10 &nbsp; <i style="background: #FFFFE0; width:20px; height:20px; float:right; margin-top:3px;"></i><br>
         </div>
         '''
        m2.get_root().html.add_child(folium.Element(custom_legend_html))

        gradient_legend_html = '''
        <div style="position: fixed; top: 50px; right: 50px; width: 200px; height: 20px; 
        background: linear-gradient(to right, #FFFFE0, #F0E68C, #DAA520, #CD5C5C, #8B0000);
        border: 2px solid grey; z-index: 9999; font-size: 12px;
        text-align: center; color: black; border-radius: 5px;
        box-shadow: 3px 3px 3px rgba(0,0,0,0.2);">
            <span style="float: left; padding-left: 5px;">0</span>
            <span style="float: right; padding-right: 5px;">>1000</span>
            <div style="clear: both;"></div>
            <b>Publications by Country</b>
        </div>
        '''
        m2.get_root().html.add_child(folium.Element(gradient_legend_html))

        return JsonResponse({'map_html': m2._repr_html_()})

def summary(request):
    """
    Main view for the summary page
    """
    # Basic counts
    unique_genes = Geneagmp.objects.exclude(gene_id__iexact='').exclude(gene_id__iexact="nan").values('gene_id').distinct()
    gene_count = unique_genes.count()
    drug_count = Drugagmp.objects.exclude(drug_bank_id__iexact='').exclude(drug_bank_id__iexact="nan").values('drug_bank_id').distinct().count()
    variant_count = Variantagmp.objects.exclude(rs_id__iexact='').exclude(rs_id__iexact="nan").values('rs_id').distinct().count()
    disease_count = Variantagmp.objects.values('phenotypeagmp__name').distinct().count()
    publication_count = Studyagmp.objects.exclude(publication_id__iexact='').exclude(publication_id__iexact="nan").values('publication_id').distinct().count()

    # Optimized queries for graphs
    qs_drug = (
        Drugagmp.objects.exclude(drug_name="nan")
        .values('drug_name')
        .annotate(frequency=Count('drugs'))
        .order_by('-frequency')[:10]
    )

    qs_gene = (
        Geneagmp.objects.exclude(gene_name="nan")
        .values('gene_id')
        .annotate(frequency=Count('variantagmp__studyagmp'))
        .order_by('-frequency')[:10]
    )

    qs_variant = (
        Variantagmp.objects.exclude(rs_id="nan")
        .values('rs_id')
        .annotate(frequency=Count('studyagmp'))
        .order_by('-frequency')[:10]
    )

    qs_disease = (
        Phenotypeagmp.objects.exclude(variantagmp__source_db="PharmGKB")
        .exclude(variantagmp__source_db="nan")
        .values('name')
        .annotate(frequency=Count('variantagmp'))
        .order_by('-frequency')[:10]
    )

    context = {
        'gene_count': gene_count,
        'publication_count': publication_count,
        'drug_count': drug_count,
        'variant_count': variant_count,
        'disease_count': disease_count,
        'qs_drug': qs_drug,
        'qs_gene': qs_gene,
        'qs_variant': qs_variant,
        'qs_disease': qs_disease,
        'study_types': ['All', 'GWAS', 'Case Report','Candidate Gene','WES/WGS','Clinical Trial','Other']
    }

    return render(request, 'summary.html', context)






def outreach(request):
    return render(request, 'outreach.html')


def contact(request):
    return render(request, 'contact.html')


def disclaimer(request):
    return render(request, 'disclaimer.html')


def faqs(request):
    return render(request, 'faqs.html')


def tools_pipelines(request):
    return render(request, 'tools_pipelines.html')


def databases(request):
    return render(request, 'resources.html')


def online_courses(request):
    return render(request, 'online_courses.html')


def help(request):
    return render(request, 'help.html')


def tutorial(request):
    return render(request, 'tutorial.html')


def home(request):
    return render(request, 'home.html')
# def download_file(request, file_name):
#     response = FileResponse(open(f"{file_name}", 'rb'))
#     return response
def test_data_table(request):
    return render(request, 'test_data_table.html')
