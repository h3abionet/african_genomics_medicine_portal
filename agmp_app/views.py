from urllib.parse import DefragResult
from django.shortcuts import render, HttpResponse, redirect
from django.http import FileResponse

from django.core import serializers
from itertools import chain
from .forms import SearchForm,ModelSearchForm
import json
import folium
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

from django.core.cache import cache

 #current search view
def search_view(request):

    form = ModelSearchForm(request.GET)
    model_selection = ""

    if form.is_valid():
        model_selection = form.cleaned_data['model_selection']
        search_query = form.cleaned_data['search_query']
        #cache code
        cache_key = f"variantagmp_{search_query}"
        results = cache.get(cache_key)
        #cache code

     
        if model_selection == 'variantagmp':
            results = Variantagmp.objects.filter(rs_id__icontains=search_query)
            #cache code bit
            cache.set(cache_key, results, timeout=300)
            #cache code bit
        elif model_selection == 'geneagmp':
            results = Geneagmp.objects.filter(gene_id__icontains=search_query)

        elif model_selection == 'drugagmp':
            results = Drugagmp.objects.filter(drug_name__icontains=search_query)
            
        elif model_selection == 'disease':
           results = Variantagmp.objects.select_related().exclude(source_db="PharmGKB").filter(phenotypeagmp__name__icontains=search_query).values("phenotypeagmp__name").distinct()
    else:
        results = []


    return render(request, 'search_list_template.html', {'form': form, 'results': results, 'model_selection': model_selection})

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
                results = Drugagmp.objects.filter(drug_name__icontains=search_query)
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
  
 #################### PharmacoGene Associations as SAMPLE to fix issues ################################
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
        
        context["data"] = Geneagmp.objects.get(gene_id = gene_id)
       

        #exclude multiple fields as an example
        exclude_list = ['A', 'B', 'C']
        context['object_list'] = VariantStudyagmp.objects.filter(
            variantagmp__geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id))).exclude(variantagmp__source_db="DisGeNET")
        

        context['object_list_diseases'] = VariantStudyagmp.objects.filter(
            variantagmp__geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id))).exclude(variantagmp__source_db="PharmGKB")
        
        return context

 #################### Gene Drug Associations ################################


 #################### Var Drug Associations ################################
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
            variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id))).exclude(variantagmp__source_db="DisGeNET") 
        


        return context

 #################### Variant Disease Associations ################################

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
            variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id))).exclude(variantagmp__source_db="PharmGKB")
        


        return context
    

  #################### DRUG searchs for Variant drug Associations ################################

class VariantDrugAssociationDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'VariantDrugAssociation.html'
    pk_url_kwarg = 'drug_id'

    def get_object(self):
        drug_id = self.kwargs.get(self.pk_url_kwarg)

        data00 = Drugagmp.objects.filter(drug_id=drug_id)
        # print(data) # for testing purposes
        return data00
    
    def get_context_data(self, **kwargs):
        context = super(VariantDrugAssociationDetailView, self).get_context_data(**kwargs)
        drug_id = self.kwargs.get(self.pk_url_kwarg)
     
        context['data'] = Drugagmp.objects.get(
            drug_id=drug_id)
        #content to display
        variant = Drugagmp.objects.filter(drug_id=drug_id)

       
        context['object_list'] = VariantStudyagmp.objects.filter(
            variantagmp__drugagmp__drug_id__iregex=r"\b{0}\b".format(str(drug_id)))
        # .exclude(variantagmp__source_db="PharmGKB")
        


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
            variantagmp__phenotypeagmp__name__iregex=r"\b{0}\b".format(str(phenotypeagmp__name))).exclude(variantagmp__source_db="PharmGKB")
       
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



def summary(request):
    # Basic counts
    gene_count = Geneagmp.objects.count()
    drug_count = Drugagmp.objects.exclude(drug_name__iexact="nan").count()
    variant_count = Variantagmp.objects.count()
    disease_count = Variantagmp.objects.exclude(source_db="PharmGKB").count()

    # Optimized query for top 10 drugs by publications
    topten_drugz = Drugagmp.objects.annotate(num_pubs=Count('drugs')).order_by('-num_pubs')[:10]

    # Optimized query for top 10 genes by publications
    topten_genez = Geneagmp.objects.annotate(num_pubs=Count('variantagmp')).order_by('-num_pubs')[:10]

    # Optimized top 10 querysets
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
        Phenotypeagmp.objects.exclude(variantagmp__source_db="PharmGKB").exclude(variantagmp__source_db="nan")
        .values('name')
        .annotate(frequency=Count('variantagmp'))
        .order_by('-frequency')[:10]
    )

    # Function to retrieve and clean location data
    def get_location_data(lat_field, lon_field):
        locations = VariantStudyagmp.objects.exclude(
            Q(**{f'{lon_field}__isnull': True}) | Q(**{f'{lon_field}__exact': ''}) |
            Q(**{f'{lat_field}__isnull': True}) | Q(**{f'{lat_field}__exact': ''})
        ).values('studyagmp__publication_id', lat_field, lon_field)

        logging.debug(f"Retrieved {lat_field}, {lon_field} locations: {list(locations)}")

        renamed_queryset = locations.annotate(
            latitude=F(lat_field),
            longitude=F(lon_field)
        ).values('latitude', 'longitude')

        return renamed_queryset

    # Collect all location data
    location_fields = [
        ('latitude_01', 'longitude_01'), ('latitude_02', 'longitude_02'),
        ('latitude_03', 'longitude_03'), ('latitude_04', 'longitude_04'),
        ('latitude_05', 'longitude_05'), ('latitude_06', 'longitude_06'),
        ('latitude_07', 'longitude_07'), ('latitude_08', 'longitude_08'),
        ('latitude_09', 'longitude_09'), ('latitude_10', 'longitude_10'),
        ('latitude_11', 'longitude_11')
    ]

    locations = [get_location_data(lat, lon) for lat, lon in location_fields]

    # Flatten the list of location querysets
    flattened_locations = [item for sublist in locations for item in sublist]

    # Log combined locations
    logging.debug(f"Combined locations: {flattened_locations}")

    records = flattened_locations
    count_per_coordinates = defaultdict(int)
    for record in records:
        coordinates = (record["latitude"], record["longitude"])
        count_per_coordinates[coordinates] += 1

    coord_per_publications_dict = count_per_coordinates.items()

    m = folium.Map(location=[-4.0335, 21.7501], zoom_start=3)
    data_set = coord_per_publications_dict
    for coordinates, value in data_set:
        try:
            clean_latitude = float(coordinates[0])
            clean_longitude = float(coordinates[1])
            popup_text = "Publications"
            popup_number = value  # Replace with your desired number
            popup_content = f"{popup_text}: {popup_number}"
            popup = folium.Popup(popup_content, parse_html=True)
            folium.Marker([clean_latitude, clean_longitude], popup=popup).add_to(m)
        except ValueError:
            logging.warning(f"Skipping invalid coordinates: {coordinates}")

    m = m._repr_html_()

    context = {
        'gene_count': gene_count,
        'drug_count': drug_count,
        'variant_count': variant_count,
        'disease_count': disease_count,
        'qs_drug': qs_drug,
        'qs_gene': qs_gene,
        'qs_variant': qs_variant,
        'qs_disease': qs_disease,
        'locations': flattened_locations,
        'coord_per_publications_dict': coord_per_publications_dict,
        'map': m,
        'data_set': data_set
    }

    return render(request, 'summary.html', context)



########### old summary view ###########
# def summary(request):

#     gene_count=Geneagmp.objects.all().count()
#     drug_count=Drugagmp.objects.all().count()
#     variant_count=Variantagmp.objects.all().count()
#     disease_count=Variantagmp.objects.select_related().exclude(source_db="PharmGKB").count()
#     #test qset
#     topten_drugz = Drugagmp.objects.all().annotate(num_pubs=Count('drugs')).order_by('-num_pubs')[:10]
#     topten_genez = Geneagmp.objects.all().annotate(num_pubs=Count('variantagmp')).order_by('-num_pubs')[:10]
#     #production qset
#     qs_drug = Drugagmp.objects.exclude(drug_name="").annotate(frequency=Count('drugs')).order_by("-frequency")[:10]
#     qs_gene = Geneagmp.objects.all().annotate(frequency=Count('variantagmp__studyagmp')).order_by("-frequency")[:10]
#     qs_variant = Variantagmp.objects.all().values('rs_id').annotate(frequency=Count('studyagmp')).order_by("-frequency")[:10]
#     qs_disease = Phenotypeagmp.objects.exclude(variantagmp__source_db="PharmGKB").values('name').annotate(frequency=Count('variantagmp')).order_by("-frequency")[:10]

#     # Map Data # Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data
    
#     locations_01 = VariantStudyagmp.objects.all().annotate(dcount=Count('studyagmp__publication_id')).exclude(Q(longitude_01__isnull=True) | Q(longitude_01__exact ='')).exclude(Q(latitude_01__isnull=True) | Q(latitude_01__exact ='')).values('studyagmp__publication_id','latitude_01','longitude_01')
#     renamed_queryset_01 = (locations_01.values('studyagmp__publication_id').annotate(
#     latitude=F('latitude_01'),
#     longitude=F('longitude_01')
#     ).values('latitude', 'longitude'))

#     locations_02 = VariantStudyagmp.objects.all().annotate(dcount=Count('studyagmp__publication_id')).exclude(Q(longitude_02__isnull=True) | Q(longitude_02__exact ='')).exclude(Q(latitude_02__isnull=True) | Q(latitude_02__exact ='')).values('studyagmp__publication_id','latitude_02','longitude_02')
#     renamed_queryset_02 = locations_02.values('studyagmp__publication_id').annotate(
#     latitude=F('latitude_02'),
#     longitude=F('longitude_02')
#     ).values('latitude', 'longitude')

#     locations_03 = VariantStudyagmp.objects.all().annotate(dcount=Count('studyagmp__publication_id')).exclude(Q(longitude_03__isnull=True) | Q(longitude_03__exact ='')).exclude(Q(latitude_03__isnull=True) | Q(latitude_03__exact ='')).values('studyagmp__publication_id','latitude_03','longitude_03')
#     renamed_queryset_03 = locations_03.values('studyagmp__publication_id').annotate(
#     latitude=F('latitude_03'),
#     longitude=F('longitude_03')
#     ).values('latitude', 'longitude')

#     locations_04 = VariantStudyagmp.objects.all().annotate(dcount=Count('studyagmp__publication_id')).exclude(Q(longitude_04__isnull=True) | Q(longitude_04__exact ='')).exclude(Q(latitude_04__isnull=True) | Q(latitude_04__exact ='')).values('studyagmp__publication_id','latitude_04','longitude_04')
#     renamed_queryset_04 = locations_04.values('studyagmp__publication_id').annotate(
#     latitude=F('latitude_04'),
#     longitude=F('longitude_04')
#     ).values('latitude', 'longitude')

#     locations_05 = VariantStudyagmp.objects.all().annotate(dcount=Count('studyagmp__publication_id')).exclude(Q(longitude_05__isnull=True) | Q(longitude_05__exact ='')).exclude(Q(latitude_05__isnull=True) | Q(latitude_05__exact ='')).values('studyagmp__publication_id','studyagmp__publication_id','latitude_05','longitude_05')
#     renamed_queryset_05 = locations_05.values('studyagmp__publication_id').annotate(
#     latitude=F('latitude_05'),
#     longitude=F('longitude_05')
#     ).values('latitude', 'longitude')

#     locations_06 = VariantStudyagmp.objects.all().annotate(dcount=Count('studyagmp__publication_id')).exclude(Q(longitude_06__isnull=True) | Q(longitude_06__exact ='')).exclude(Q(latitude_06__isnull=True) | Q(latitude_06__exact ='')).values('studyagmp__publication_id','latitude_06','longitude_06')
#     renamed_queryset_06 = locations_06.values('studyagmp__publication_id').annotate(
#     latitude=F('latitude_06'),
#     longitude=F('longitude_06')
#     ).values('latitude', 'longitude')

#     locations_07 = VariantStudyagmp.objects.all().annotate(dcount=Count('studyagmp__publication_id')).exclude(Q(longitude_07__isnull=True) | Q(longitude_07__exact ='')).exclude(Q(latitude_07__isnull=True) | Q(latitude_07__exact ='')).values('studyagmp__publication_id','latitude_07','longitude_07')
#     renamed_queryset_07 = locations_07.annotate(
#     latitude=F('latitude_07'),
#     longitude=F('longitude_07')
#     ).values('latitude', 'longitude')

#     locations = list(renamed_queryset_01) + list(renamed_queryset_02) +  list(renamed_queryset_03) +  list(renamed_queryset_04) +  list(renamed_queryset_05)  +  list(renamed_queryset_06)  +  list(renamed_queryset_07)

#     combined_queryset = renamed_queryset_01 | renamed_queryset_02 | renamed_queryset_03 | renamed_queryset_04 | renamed_queryset_05 | renamed_queryset_06 | renamed_queryset_07

#     records = locations
#     count_per_coordinates = defaultdict(int)
#     for record in records:
#         coordinates = (record["latitude"], record["longitude"])
#         count_per_coordinates[coordinates] += 1
    

#     for coordinates, count in count_per_coordinates.items():
#         latitude, longitude = coordinates
#         # print(f"Latitude: {latitude}, Longitude: {longitude} - Publications: {count}")

#     coord_per_publications_dict=count_per_coordinates.items()

#     m = folium.Map(location=[-4.0335, 21.7501], zoom_start=3)
#     data_set = coord_per_publications_dict
#     for coordinates, value in data_set:
#         latitude, longitude = coordinates
#         clean_latitude = float(coordinates[0])
#         clean_longitude = float(coordinates[1])
#         # print(f"Lllatitude: {clean_latitude}, Llllongitude: {clean_longitude}, Value: {value}")
#         popup_text = "Publications"
#         popup_number = value  # Replace with your desired number
#         popup_content = f"{popup_text}: {popup_number}"
#         popup = folium.Popup(popup_content, parse_html=True)
#         folium.Marker([clean_latitude, clean_longitude], popup=popup).add_to(m)
    

#     m = m._repr_html_()
    
#     # Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data
  
#     context = { 'gene_count': gene_count,'drug_count': drug_count,'variant_count': variant_count,'disease_count': disease_count,
#                'qs_drug': qs_drug,'qs_gene': qs_gene,'qs_variant': qs_variant,'qs_disease': qs_disease, 'locations':locations ,'coord_per_publications_dict':coord_per_publications_dict,'map': m,'data_set':data_set}

    
#     return render(request, 'summary.html', context , )
########### old summary view ###########


def resources(request):
    return render(request, 'resources.html')


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
