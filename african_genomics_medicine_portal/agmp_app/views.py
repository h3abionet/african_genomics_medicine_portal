from urllib.parse import DefragResult
from django.shortcuts import render, HttpResponse, redirect,  get_object_or_404
from django.http import FileResponse
from django.core import serializers
from itertools import chain
from .models import Drugagmp, Geneagmp, Studyagmp, Variantagmp, VariantStudyagmp, Phenotypeagmp
from agmp_app.models import *
from django.db.models import Avg, Min, Max, Count, Q, F
from collections import Counter
from django.views.generic.detail import DetailView
from django.views.generic import ListView
from .forms import SearchForm
from django.http import JsonResponse

from collections import defaultdict
import json

import folium

import re








def summary(request):
    gene_count=Geneagmp.objects.all().count()
    drug_count=Drugagmp.objects.all().count()
    variant_count=Variantagmp.objects.all().count()
    disease_count=Variantagmp.objects.select_related().exclude(source_db="PharmGKB").distinct().count()
    #test qset
    topten_drugz = Drugagmp.objects.all().annotate(num_pubs=Count('drugs')).order_by('-num_pubs')[:10]
    topten_genez = Geneagmp.objects.all().annotate(num_pubs=Count('variantagmp')).order_by('-num_pubs')[:10]
    #production qset
    qs_drug = Drugagmp.objects.exclude(drug_name="").annotate(frequency=Count('drugs')).order_by("-frequency")[:10]
    qs_gene = Geneagmp.objects.all().annotate(frequency=Count('variantagmp__studyagmp')).order_by("-frequency")[:10]
    qs_variant = Variantagmp.objects.all().values('rs_id').annotate(frequency=Count('studyagmp')).order_by("-frequency")[:10]
    qs_disease = Phenotypeagmp.objects.exclude(variantagmp__source_db="PharmGKB").values('name').annotate(frequency=Count('variantagmp')).order_by("-frequency")[:10]

    # Map Data # Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data
    
    locations_01 = VariantStudyagmp.objects.all().exclude(longitude_01__exact='').exclude(latitude_01__exact='').distinct('studyagmp__publication_id').values('studyagmp__publication_id','latitude_01','longitude_01')
    renamed_queryset_01 = locations_01.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_01'),
    longitude=F('longitude_01')
    ).values('latitude', 'longitude')

    locations_02 = VariantStudyagmp.objects.all().exclude(longitude_02__exact='').exclude(latitude_02__exact='').distinct('studyagmp__publication_id').values('studyagmp__publication_id','latitude_02','longitude_02')
    renamed_queryset_02 = locations_02.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_02'),
    longitude=F('longitude_02')
    ).values('latitude', 'longitude')

    locations_03 = VariantStudyagmp.objects.all().exclude(longitude_03__exact='').exclude(latitude_03__exact='').distinct('studyagmp__publication_id').values('studyagmp__publication_id','latitude_03','longitude_03')
    renamed_queryset_03 = locations_03.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_03'),
    longitude=F('longitude_03')
    ).values('latitude', 'longitude')

    locations_04 = VariantStudyagmp.objects.all().exclude(longitude_04__exact='').exclude(latitude_04__exact='').distinct('studyagmp__publication_id').values('studyagmp__publication_id','latitude_04','longitude_04')
    renamed_queryset_04 = locations_04.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_04'),
    longitude=F('longitude_04')
    ).values('latitude', 'longitude')

    locations_05 = VariantStudyagmp.objects.all().exclude(longitude_05__exact='').exclude(latitude_05__exact='').distinct('studyagmp__publication_id').values('studyagmp__publication_id','studyagmp__publication_id','latitude_05','longitude_05')
    renamed_queryset_05 = locations_05.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_05'),
    longitude=F('longitude_05')
    ).values('latitude', 'longitude')

    locations_06 = VariantStudyagmp.objects.all().exclude(longitude_06__exact='').exclude(latitude_06__exact='').distinct('studyagmp__publication_id').values('studyagmp__publication_id','latitude_06','longitude_06')
    renamed_queryset_06 = locations_06.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_06'),
    longitude=F('longitude_06')
    ).values('latitude', 'longitude')

    locations_07 = VariantStudyagmp.objects.all().exclude(longitude_07__exact='').exclude(latitude_07__exact='').distinct('studyagmp__publication_id').values('studyagmp__publication_id','latitude_07','longitude_07')
    renamed_queryset_07 = locations_07.annotate(
    latitude=F('latitude_07'),
    longitude=F('longitude_07')
    ).values('latitude', 'longitude')

    locations = list(renamed_queryset_01) + list(renamed_queryset_02) +  list(renamed_queryset_03) +  list(renamed_queryset_04) +  list(renamed_queryset_05)  +  list(renamed_queryset_06)  +  list(renamed_queryset_07)


    records = locations
    count_per_coordinates = defaultdict(int)
    for record in records:
        coordinates = (record["latitude"], record["longitude"])
        count_per_coordinates[coordinates] += 1
    

    for coordinates, count in count_per_coordinates.items():
        latitude, longitude = coordinates
        # print(f"Latitude: {latitude}, Longitude: {longitude} - Publications: {count}")

    coord_per_publications_dict=count_per_coordinates.items()

    m = folium.Map(location=[-4.0335, 21.7501], zoom_start=3)
    data_set = coord_per_publications_dict
    for coordinates, value in data_set:
        latitude, longitude = coordinates
        clean_latitude = (coordinates[0])
        clean_longitude = (coordinates[1])

        float_clean_latitude = float(clean_latitude)
        float_clean_longitude = float(clean_longitude)
        # print(f"Lllatitude: {clean_latitude}, Llllongitude: {clean_longitude}, Value: {value}")
        popup_text = "Publications"
        popup_number = value  # Replace with your desired number
        popup_content = f"{popup_text}: {popup_number}"
        popup = folium.Popup(popup_content, parse_html=True)
        folium.Marker([float_clean_latitude, float_clean_longitude], popup=popup).add_to(m)
    

    m = m._repr_html_()
    
    # Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data
  
    context = { 'gene_count': gene_count,'drug_count': drug_count,'variant_count': variant_count,'disease_count': disease_count,
               'qs_drug': qs_drug,'qs_gene': qs_gene,'qs_variant': qs_variant,'qs_disease': qs_disease, 'locations':locations ,'coord_per_publications_dict':coord_per_publications_dict,'map': m,'data_set':data_set}
    

    return render(request, 'summary.html', context , )


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
                     
            return render(request, 'search_form.html', {'form': form, 'results': results, 'search_option':search_option })
    else:
        form = SearchForm()
        
    return render(request, 'search_form.html', {'form': form})


def autocomplete_search(request):
    if request.method == 'POST':
        form = SearchForm(request.POST)
        if form.is_valid():
            query = request.GET.get('term', '')
            # search_query = form.cleaned_data['search_query']
            results =  Variantagmp.objects.select_related().exclude(source_db="PharmGKB").filter(phenotypeagmp__name__icontains=search_query).values("phenotypeagmp__name").distinct()
            suggestions = [result.phenotypeagmp__name for result in results]
            return JsonResponse(suggestions, safe=False)


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
    



# Variant Details view
def variant_detail_view(request, pk):
    variant_item = Variantagmp.objects.get(id=pk)
    context = {'variant_item': variant_item,}
    return render(request, 'variant_detail.html', context)


def FilterView(request):
    qs_variant = Variantagmp.objects.select_related().all() 
    variant_contains_query = request.GET.get('variant_contains')
    if variant_contains_query != '' and variant_contains_query is not None:
        qs_variant = qs_variant.filter(rs_id__icontains=variant_contains_query)



    context = {
  

        'qs_variant':qs_variant,
      
    
    
    }
    return render(request, "search_variant.html",context)

def FilterViewDrug(request):

    qs_drug = Drugagmp.objects.select_related().all() 
    drug_contains_query = request.GET.get('drug_contains')
    if drug_contains_query != '' and drug_contains_query is not None:
        qs_drug = qs_drug.filter(drug_name__icontains=drug_contains_query)



    context = {
  

        'qs_drug':qs_drug,
      
    
    
    }

    return render(request, "search_drug.html",context)



def FilterViewGene(request):

    qs_gene = Geneagmp.objects.select_related().all() 
    gene_contains_query = request.GET.get('gene_contains')
    if gene_contains_query != '' and gene_contains_query is not None:
        qs_gene = qs_gene.filter(gene_name__icontains=gene_contains_query)



    context = {
  

        'qs_gene':qs_gene,
      
    
    
    }

    return render(request, "search_gene.html",context)


def FilterViewDisease(request):

    qs_disease = Variantagmp.objects.select_related().exclude(source_db="PharmGKB")
    disease_contains_query = request.GET.get('disease_contains')
    if disease_contains_query != '' and disease_contains_query is not None:
        qs_disease = qs_disease.filter(phenotypeagmp__name__icontains=disease_contains_query)


    context = {
  

        'qs_disease':qs_disease,
    
    
    
    }

    return render(request, "search_disease.html",context)


def about(request):
    return render(request, 'about.html')


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

def handler404(request, exception=None):
    page_title = "404, Page not found !"
    return render(request, '404.html', {'page_title': page_title, })


