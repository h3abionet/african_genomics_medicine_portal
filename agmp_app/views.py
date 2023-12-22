from urllib.parse import DefragResult
from django.shortcuts import render, HttpResponse, redirect
from django.http import FileResponse

from django.core import serializers
from itertools import chain

from .models import disease, pharmacogenes, drug, snp as SnpModel, star_allele, study
from .forms import PostForm, SearchForm,ModelSearchForm
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

def search_view(request):
    form = ModelSearchForm(request.GET)
    model_selection = ""

    if form.is_valid():
        model_selection = form.cleaned_data['model_selection']
        search_query = form.cleaned_data['search_query']

        # print(model_selection)
        # print(search_query)
     
        if model_selection == 'variantagmp':
            results = Variantagmp.objects.filter(rs_id__icontains=search_query)

        elif model_selection == 'geneagmp':
            results = Geneagmp.objects.filter(gene_id__icontains=search_query) 

        elif model_selection == 'drugagmp':
            results = Drugagmp.objects.filter(drug_name__icontains=search_query)
            
        elif model_selection == 'disease':
           results = Variantagmp.objects.select_related().exclude(source_db="PharmGKB").filter(phenotypeagmp__name__icontains=search_query).values("phenotypeagmp__name").distinct()
    else:
        results = []
     


    # return HttpResponse('Hello, world!')

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


def search(request):
    form = PostForm(
        initial={
            'gene_name': '',
            # 'protein': '',
            'function': ''
        }
    )
    return render(request, 'search.html', {"form": form})


def _get_gene_page(query):
    genes = pharmacogenes.objects.filter(id__exact=query).values()
    details = dict()
    details['name'] = genes[0].get('gene_name')
    details['external_id'] = genes[0].get('uniprot_id')
    details['description'] = genes[0].get('function')
    details['snps_drugs'] = []
    details['star_alleles_drugs'] = []
    details['snp_diseases'] = []

    for p in pharmacogenes.objects.raw(" SELECT agmp_app_snp.id, agmp_app_snp.rs_id, agmp_app_snp.snp_id, agmp_app_snp.gene_id, \
        agmp_app_drug.drug_bank_id, agmp_app_snp.p_value, agmp_app_snp.allele, agmp_app_snp.association_with, agmp_app_snp.region, agmp_app_pharmacogenes.gene_name, \
        agmp_app_drug.drug_name, agmp_app_study.reference_id, agmp_app_snp.country_of_participants FROM agmp_app_snp \
INNER JOIN agmp_app_drug on agmp_app_drug.id = agmp_app_snp.drug_id \
INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id \
INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id \
AND agmp_app_snp.gene_id = %s AND lower(agmp_app_snp.source) like 'pharmgkb%%';", [query]):
        details['snps_drugs'].append(p)

    # star alleles drugs
    for p in pharmacogenes.objects.raw("SELECT agmp_app_star_allele.id, agmp_app_star_allele.star_id, agmp_app_star_allele.star_annotation, \
    agmp_app_star_allele.allele, agmp_app_star_allele.gene_id, agmp_app_star_allele.allele, agmp_app_star_allele.phenotype, \
    agmp_app_pharmacogenes.gene_name, agmp_app_drug.drug_name, agmp_app_star_allele.p_value, agmp_app_drug.drug_bank_id, \
    agmp_app_study.reference_id, agmp_app_star_allele.country_of_participants, \
    agmp_app_star_allele.region FROM agmp_app_star_allele \
INNER JOIN agmp_app_drug on agmp_app_drug.id = agmp_app_star_allele.drug_id \
INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_star_allele.gene_id \
INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_star_allele.reference_id \
AND agmp_app_star_allele.gene_id = %s;", [query]):
        details['star_alleles_drugs'].append(p)

    # snp diseases drugs
    for p in pharmacogenes.objects.raw("SELECT agmp_app_snp.id, agmp_app_snp.rs_id, agmp_app_snp.snp_id, agmp_app_snp.gene_id, \
        agmp_app_snp.p_value, agmp_app_snp.allele, agmp_app_snp.association_with, agmp_app_snp.region, agmp_app_pharmacogenes.gene_name, \
        agmp_app_study.reference_id, agmp_app_snp.country_of_participants FROM agmp_app_snp \
INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id \
INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id \
AND agmp_app_snp.gene_id = %s AND lower(agmp_app_snp.source) like 'disgenet%%';", [query]):
        details['snp_diseases'].append(p)
    return details


def search_details(request, search_type, query_id):
    '''
    Receive query parameters from search page to fetch
    database specific results
    '''
    variant_drug = []
    gene_list = None
    gene_drug = []
    gene_details = dict()
    disease_list = []
    # query incoming request based on a drug
    if search_type == 'gene-drug' and 'gene' in query_id.lower():
        detail_view = 'gene_details.html'
        gene_details = _get_gene_page(query_id)
    elif search_type == 'gene-drug' and 'drug' in query_id.lower():
        detail_view = 'search_details.html'
        for p in pharmacogenes.objects.raw("""
         SELECT agmp_app_drug.drug_bank_id AS id,
            agmp_app_drug.drug_name,
            agmp_app_drug.state,
            agmp_app_drug.indication,
            agmp_app_drug.iupac_name,
            agmp_app_snp.rs_id,
            agmp_app_snp.p_value,
            agmp_app_snp.region,
            agmp_app_pharmacogenes.gene_name,
            agmp_app_pharmacogenes.id AS gene_id,
            agmp_app_study.title,
            agmp_app_study.reference_id
            FROM agmp_app_drug
 INNER JOIN agmp_app_snp on agmp_app_drug.id = agmp_app_snp.drug_id
 INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id
 INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id
 AND agmp_app_drug.id = %s;""", [query_id]):
            variant_drug.append(p)

    if (search_type == 'variant-drug') and 'snp' in query_id.lower():
        detail_view = 'search_details.html'
        for p in pharmacogenes.objects.raw(" SELECT agmp_app_snp.id, agmp_app_snp.rs_id, \
            country_of_participants, agmp_app_pharmacogenes.id AS gene_id, \
            agmp_app_study.title, agmp_app_study.reference_id, p_value, region, gene_name, drug_name FROM agmp_app_snp \
 INNER JOIN agmp_app_drug on agmp_app_drug.id = agmp_app_snp.drug_id \
 INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id \
 INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id \
 AND agmp_app_snp.snp_id =%s;", [query_id]):
            variant_drug.append(p)

    if (search_type == 'variant-drug') and 'drug' in query_id.lower():
        detail_view = 'search_details.html'
        for p in pharmacogenes.objects.raw(" SELECT \
            agmp_app_snp.id, \
            rs_id, \
            allele, \
            association_with, \
            p_value, \
            source, \
            region, \
            country_of_participants, \
            drug_name, \
	        agmp_app_pharmacogenes.gene_name, \
            agmp_app_pharmacogenes.id AS gene_id, \
            agmp_app_study.type, \
            agmp_app_study.reference_id, \
            agmp_app_study.title \
            FROM agmp_app_snp \
        INNER JOIN agmp_app_drug on agmp_app_drug.id = agmp_app_snp.drug_id \
        INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id \
        INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id \
        AND agmp_app_drug.id = %s;", [query_id]):
            variant_drug.append(p)

    if (search_type == 'variant-disease') and 'snp' in query_id.lower():
        detail_view = 'search_details.html'
        for p in pharmacogenes.objects.raw(""" SELECT
agmp_app_snp.id,
agmp_app_snp.snp_id,
rs_id,
allele,
association_with,
p_value,
source,
region,
country_of_participants,
disease_id,
agmp_app_pharmacogenes.gene_name,
agmp_app_pharmacogenes.id AS gene_id,
agmp_app_disease.disease_name,
agmp_app_study.type,
agmp_app_study.reference_id,
agmp_app_study.title
FROM agmp_app_snp
INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id
INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id
INNER JOIN agmp_app_disease on agmp_app_disease.id = agmp_app_snp.disease_id
AND agmp_app_snp.snp_id = %s;""", [query_id]):
            disease_list.append(p)

    if (search_type == 'variant-disease') and 'dis' in query_id.lower():
        detail_view = 'search_details.html'
        for p in pharmacogenes.objects.raw(""" SELECT
agmp_app_snp.id,
rs_id,
allele,
association_with,
p_value,
source,
region,
country_of_participants,
disease_id,
agmp_app_pharmacogenes.gene_name,
agmp_app_pharmacogenes.id AS gene_id,
agmp_app_disease.disease_name,
agmp_app_study.type,
agmp_app_study.reference_id,
agmp_app_study.title
FROM agmp_app_snp
INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id
INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id
INNER JOIN agmp_app_disease on agmp_app_disease.id = agmp_app_snp.disease_id
AND agmp_app_disease.id =  %s;""", [query_id]):
            disease_list.append(p)

    # print(variant_drug)
    # print(gene_list)
    # print(gene_drug)
    # print(disease_list)
    # print(gene_details)

    return render(
        request, detail_view, {
            # 'db_name': db_name,
            'search_type': search_type,
            'query_id': query_id,
            'variant_drug': variant_drug,
            'genes': gene_list,
            'gene_drug': gene_drug,
            'gene_details': gene_details,
            'diseases': disease_list,
        }
    )


def _fetch_disease(diseases):
    '''
    :param list item_list: a list of item names to fetch from disease table
    :return dict
    '''
    ret = []
    for disease in diseases:
        disease_object = dict()
        disease_object['key'] = 'ds'
        disease_object['detail'] = []

        disease_object['id'] = disease.get('id')
        disease_object['name'] = disease.get('disease_name')
        ret.append(disease_object)
    print('DISEASE ', ret)
    return ret


def _fetch_drug(drugs):
    '''
    :param list item_list: a list of item names to fetch from drug table
    :return dict
    '''
    ret = []
    # drugs = drug.objects.filter(drug_name__contains= query).values()
    for drug in drugs:
        drug_object = dict()
        drug_object['key'] = 'dg'
        drug_object['detail'] = [
            "Drug Bank ID: <a target='_blank' href='https://www.drugbank.ca/drugs/{0}'>{1}</a>".format(
                drug.get('drug_bank_id'), drug.get('drug_bank_id')),
            'State: {0}'.format(drug.get('state'))]

        drug_object['id'] = drug['id']
        drug_object['name'] = drug['drug_name']
        drug_object['drug_bank_id'] = drug['drug_bank_id']
        drug_object['state'] = drug['state']
        drug_object['indication'] = drug['indication']
        drug_object['iupac_name'] = drug['iupac_name']
        ret.append(drug_object)
    # print('DRUG ',ret)
    return ret


def _fetch_variant(qs):
    '''
    :param list item_list: a list of item names to fetch from snp table
    :return dict
    '''
    ret = []
    snps = SnpModel.objects.select_related(
        'gene').filter(rs_id__icontains=qs).all()
    print(snps)
    for snp in snps:
        # snp = snp.values()
        variant_object = dict()
        variant_object['key'] = 'vt'
        variant_object['detail'] = ["<b>Chromosome</b> {0}".format(
            snp.gene.chromosome_patch), "<b>Gene: {0}</b>".format(snp.gene.gene_name)]

        variant_object['id'] = snp.snp_id
        variant_object['name'] = 'rs ID: {0}'.format(snp.rs_id)
        variant_object['drug'] = snp.drug_id
        variant_object['allele'] = snp.allele
        variant_object['gene'] = snp.gene_id
        variant_object['phenotype'] = snp.association_with
        variant_object['reference'] = snp.reference_id
        variant_object['p_value'] = snp.p_value
        variant_object['source'] = snp.source
        variant_object['id_in_source'] = snp.id_in_source
        # variant_object['chromosome'] = snp['chromosome']
        ret.append(variant_object)
    # print('VARIANT ',ret)
    return ret


def _fetch_gene(genes):
    '''
    :param list item_list: a list of item names to fetch from study table
    :return dict
    '''
    ret = []
    # genes = pharmacogenes.objects.filter(gene_name__contains= query).values()
    for gene in genes:
        gene_object = dict()
        gene_object['key'] = 'ge'
        gene_object['detail'] = [
            'Chromosome {0}'.format(gene.get('chromosome_patch'))]

        gene_object['id'] = gene['id']
        gene_object['name'] = gene['gene_name']
        gene_object['function'] = gene['function']
        gene_object['uniprot_id'] = gene['uniprot_id']
        gene_object['chromosome'] = gene['chromosome_patch']
        ret.append(gene_object)
    # print('GENE ',ret)
    return ret


def _fetch_data(model, item_list):
    '''
    :param Model model: the model to fetch from
    :param list item_list: a list of item names to fetch from table
    :return dict

    harmonises the fetch data from specific tables into a
    more generic search function

    provided in the input parameters
    '''
    # TODO:
    pass


def query(request, query_string, **kwargs):
    '''
    Get search query from ajax call
    Return JSON after retrieving data from database
    '''
    # fetch the optional parameters from the request
    is_disease = int(request.GET.get('disease', 0))
    is_drug = int(request.GET.get('drug', 0))
    is_variant = int(request.GET.get('variant', 0))
    is_gene = int(request.GET.get('gene', 0))

    pass_list = []

    if request.is_ajax():
        # TODO: there must be a better way to do this
        if is_disease:
            disgenet_snps = SnpModel.objects.filter(
                source__icontains='DisGeNET')
            disgenet_snps = disgenet_snps.filter(
                association_with__icontains=query_string)
            # pass_list += _fetch_disease(disgenet_snps.values())
            pass_list += _fetch_disease(disease.objects.filter(
                disease_name__contains=query_string).values())
            print(pass_list)
        if is_drug:
            pass_list += _fetch_drug(drug.objects.filter(
                drug_name__contains=query_string).values())
        if is_variant:
            pass_list += _fetch_variant(query_string)
        if is_gene:
            pass_list += _fetch_gene(pharmacogenes.objects.filter(
                gene_name__contains=query_string).values())

    res = json.dumps(pass_list)
    mimetype = 'application/json'
    return HttpResponse(res, mimetype)


def summary(request):

    gene_count=Geneagmp.objects.all().count()
    drug_count=Drugagmp.objects.all().count()
    variant_count=Variantagmp.objects.all().count()
    disease_count=Variantagmp.objects.select_related().exclude(source_db="PharmGKB").count()
    #test qset
    topten_drugz = Drugagmp.objects.all().annotate(num_pubs=Count('drugs')).order_by('-num_pubs')[:10]
    topten_genez = Geneagmp.objects.all().annotate(num_pubs=Count('variantagmp')).order_by('-num_pubs')[:10]
    #production qset
    qs_drug = Drugagmp.objects.exclude(drug_name="").annotate(frequency=Count('drugs')).order_by("-frequency")[:10]
    qs_gene = Geneagmp.objects.all().annotate(frequency=Count('variantagmp__studyagmp')).order_by("-frequency")[:10]
    qs_variant = Variantagmp.objects.all().values('rs_id').annotate(frequency=Count('studyagmp')).order_by("-frequency")[:10]
    qs_disease = Phenotypeagmp.objects.exclude(variantagmp__source_db="PharmGKB").values('name').annotate(frequency=Count('variantagmp')).order_by("-frequency")[:10]

    # Map Data # Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data
    
    locations_01 = VariantStudyagmp.objects.all().exclude(Q(longitude_01__isnull=True) | Q(longitude_01__exact ='')).exclude(Q(latitude_01__isnull=True) | Q(latitude_01__exact ='')).values('studyagmp__publication_id','latitude_01','longitude_01')
    renamed_queryset_01 = locations_01.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_01'),
    longitude=F('longitude_01')
    ).values('latitude', 'longitude')

    locations_02 = VariantStudyagmp.objects.all().exclude(Q(longitude_02__isnull=True) | Q(longitude_02__exact ='')).exclude(Q(latitude_02__isnull=True) | Q(latitude_02__exact ='')).values('studyagmp__publication_id','latitude_02','longitude_02')
    renamed_queryset_02 = locations_02.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_02'),
    longitude=F('longitude_02')
    ).values('latitude', 'longitude')

    locations_03 = VariantStudyagmp.objects.all().exclude(Q(longitude_03__isnull=True) | Q(longitude_03__exact ='')).exclude(Q(latitude_03__isnull=True) | Q(latitude_03__exact ='')).values('studyagmp__publication_id','latitude_03','longitude_03')
    renamed_queryset_03 = locations_03.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_03'),
    longitude=F('longitude_03')
    ).values('latitude', 'longitude')

    locations_04 = VariantStudyagmp.objects.all().exclude(Q(longitude_04__isnull=True) | Q(longitude_04__exact ='')).exclude(Q(latitude_04__isnull=True) | Q(latitude_04__exact ='')).values('studyagmp__publication_id','latitude_04','longitude_04')
    renamed_queryset_04 = locations_04.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_04'),
    longitude=F('longitude_04')
    ).values('latitude', 'longitude')

    locations_05 = VariantStudyagmp.objects.all().exclude(Q(longitude_05__isnull=True) | Q(longitude_05__exact ='')).exclude(Q(latitude_05__isnull=True) | Q(latitude_05__exact ='')).values('studyagmp__publication_id','studyagmp__publication_id','latitude_05','longitude_05')
    renamed_queryset_05 = locations_05.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_05'),
    longitude=F('longitude_05')
    ).values('latitude', 'longitude')

    locations_06 = VariantStudyagmp.objects.all().exclude(Q(longitude_06__isnull=True) | Q(longitude_06__exact ='')).exclude(Q(latitude_06__isnull=True) | Q(latitude_06__exact ='')).values('studyagmp__publication_id','latitude_06','longitude_06')
    renamed_queryset_06 = locations_06.values('studyagmp__publication_id').annotate(
    latitude=F('latitude_06'),
    longitude=F('longitude_06')
    ).values('latitude', 'longitude')

    locations_07 = VariantStudyagmp.objects.all().exclude(Q(longitude_07__isnull=True) | Q(longitude_07__exact ='')).exclude(Q(latitude_07__isnull=True) | Q(latitude_07__exact ='')).values('studyagmp__publication_id','latitude_07','longitude_07')
    renamed_queryset_07 = locations_07.annotate(
    latitude=F('latitude_07'),
    longitude=F('longitude_07')
    ).values('latitude', 'longitude')

    locations = list(renamed_queryset_01) + list(renamed_queryset_02) +  list(renamed_queryset_03) +  list(renamed_queryset_04) +  list(renamed_queryset_05)  +  list(renamed_queryset_06)  +  list(renamed_queryset_07)

    combined_queryset = renamed_queryset_01 | renamed_queryset_02 | renamed_queryset_03 | renamed_queryset_04 | renamed_queryset_05 | renamed_queryset_06 | renamed_queryset_07

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
        clean_latitude = float(coordinates[0])
        clean_longitude = float(coordinates[1])
        # print(f"Lllatitude: {clean_latitude}, Llllongitude: {clean_longitude}, Value: {value}")
        popup_text = "Publications"
        popup_number = value  # Replace with your desired number
        popup_content = f"{popup_text}: {popup_number}"
        popup = folium.Popup(popup_content, parse_html=True)
        folium.Marker([clean_latitude, clean_longitude], popup=popup).add_to(m)
    

    m = m._repr_html_()
    
    # Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data# Map Data
  
    context = { 'gene_count': gene_count,'drug_count': drug_count,'variant_count': variant_count,'disease_count': disease_count,
               'qs_drug': qs_drug,'qs_gene': qs_gene,'qs_variant': qs_variant,'qs_disease': qs_disease, 'locations':locations ,'coord_per_publications_dict':coord_per_publications_dict,'map': m,'data_set':data_set}

    
    return render(request, 'summary.html', context , )

def country_summary(request):
    '''
    :return JSON of country summary
    '''
    res = []

    for p in SnpModel.objects.raw("SELECT DISTINCT id, country_of_participants, latitude, longitude, region, snp_id, \
        COUNT(country_of_participants) AS cnt FROM agmp_app_snp WHERE (latitude<>'N/A' AND longitude<>'N/A') GROUP BY country_of_participants ORDER BY cnt;"):
        res.append({

            'country': p.country_of_participants,
            'region': p.region,
            'latitude': '{:,.7f}'.format(p.latitude),
            'longitude': '{0}'.format(p.longitude),
            'snp': p.snp_id,
            'count': p.cnt

        })
    # return render(request, 'summary.html', {'json_list': res})

    res = json.dumps(res)
    mimetype = 'application/json'
    return HttpResponse(res, mimetype)


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
