import logging
import re
from urllib.parse import DefragResult
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse, Http404
from django.core import serializers
from itertools import chain
from .forms import SearchForm, ModelSearchForm
import json
import folium
from folium.plugins import HeatMap
import math
import geocoder
from folium import plugins

from agmp_app.models import *
from django.db.models import Avg, Min, Max, Count, Q, F
import pandas as pd
from collections import Counter, defaultdict
from django_pandas.io import read_frame
from django.views.generic.detail import DetailView
from django.views.generic import ListView, TemplateView
import numpy as np
import os

from django.db.models import Subquery, OuterRef
from django.conf import settings
import geopandas as gpd
from shapely.geometry import Point
from fuzzywuzzy import fuzz
from fuzzywuzzy import process

# Configure logger
logger = logging.getLogger(__name__)

# Helper function to validate rsID format
def is_valid_rs_id(rs_id):
    """Validate the format of an rsID (typically rs followed by digits)"""
    if not rs_id:
        return False
    rs_pattern = re.compile(r'^rs\d+$')
    return bool(rs_pattern.match(rs_id))

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
            elif search_option == 'Disease':
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
        
        try:
            data = Geneagmp.objects.filter(gene_id=gene_id)
            if not data.exists():
                logger.warning(f"No gene found with gene_id: {gene_id}")
                raise Http404(f"No gene found with gene_id: {gene_id}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving gene {gene_id}: {str(e)}")
            raise Http404(f"Error retrieving gene: {str(e)}")
    
    def get_context_data(self, **kwargs):
        context = super(PhamacogeneDrugAssoc, self).get_context_data(**kwargs)
        gene_id = self.kwargs.get(self.pk_url_kwarg)

        try:
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
        except Exception as e:
            logger.error(f"Error in get_context_data for gene {gene_id}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."
        
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
        
        # Validate rs_id format first
        if rs_id and not rs_id.startswith("DB") and not is_valid_rs_id(rs_id):
            logger.warning(f"Invalid rs_id format: {rs_id}")
            raise Http404(f"Invalid variant ID format: {rs_id}")

        try:
            data = Variantagmp.objects.filter(rs_id=rs_id)
            if not data.exists():
                logger.warning(f"No variant found with rs_id: {rs_id}")
                raise Http404(f"No variant found with rs_id: {rs_id}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving variant {rs_id}: {str(e)}")
            raise Http404(f"Error retrieving variant: {str(e)}")
    
    def get_context_data(self, **kwargs):
        context = super(VarDrugAssocDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        
        try:  
            context['gene_id_display'] = Variantagmp.objects.values("geneagmp__gene_id").filter(rs_id=rs_id).first()
            context['chromosome_display'] = Variantagmp.objects.values("geneagmp__chromosome").filter(rs_id=rs_id).first()
            context['rs_id_display'] = Variantagmp.objects.values("rs_id").filter(rs_id=rs_id).first()
      
            #back up query
            context['object_list'] = VariantStudyagmp.objects.filter(
                variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id))).exclude(variantagmp__source_db="DisGeNET").exclude(variantagmp__source_db="GWAS Catalog")
        except Exception as e:
            logger.error(f"Error in get_context_data for variant {rs_id}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."
        
        return context

#################### Variant Disease Associations ################################
# 02 
class VariantDiseaseAssocDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'VariantDiseaseAssocDetail.html'
    pk_url_kwarg = 'rs_id'

    def get_object(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        
        # Validate rs_id format first
        if rs_id and not rs_id.startswith("DB") and not is_valid_rs_id(rs_id):
            logger.warning(f"Invalid rs_id format: {rs_id}")
            raise Http404(f"Invalid variant ID format: {rs_id}")

        try:
            data = Variantagmp.objects.filter(rs_id=rs_id)
            if not data.exists():
                logger.warning(f"No variant found with rs_id: {rs_id}")
                raise Http404(f"No variant found with rs_id: {rs_id}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving variant {rs_id}: {str(e)}")
            raise Http404(f"Error retrieving variant: {str(e)}")
    
    def get_context_data(self, **kwargs):
        context = super(VariantDiseaseAssocDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
     
        try:
            if Variantagmp.objects.filter(rs_id=rs_id).exists():
                context['rs_id_display'] = (Variantagmp.objects.values("rs_id").filter(rs_id=rs_id))[0]
                context['gene_name_display'] = Variantagmp.objects.values("geneagmp__gene_id").filter(rs_id=rs_id).first()
                context['chromosome_display'] = Variantagmp.objects.values("geneagmp__chromosome").filter(rs_id=rs_id).first()

                context['object_list'] = VariantStudyagmp.objects.filter(
                    variantagmp__rs_id__iregex=r"(^|[^a-zA-Z0-9_]){0}([^a-zA-Z0-9_]|$)".format(re.escape(str(rs_id))),
                    variantagmp__source_db__iregex=r"^(DisGeNet|GWAS Catalog)$"
                ).exclude(variantagmp__source_db="PharmGKB")
            else:
                context['error'] = f"No information found for variant: {rs_id}"
        except Exception as e:
            logger.error(f"Error in get_context_data for variant {rs_id}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."

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
        
        # If not a DB ID, validate the rs_id format first
        if rs_id and not rs_id.startswith("DB") and not is_valid_rs_id(rs_id):
            logger.warning(f"Invalid rs_id format: {rs_id}")
            raise Http404(f"Invalid variant ID format: {rs_id}")
            
        # If the ID starts with "DB", look up by drug ID instead
        if rs_id and rs_id.startswith("DB"):
            try:
                # Find a variant associated with this drug
                drug = get_object_or_404(Drugagmp, drug_bank_id=rs_id)
                variant = Variantagmp.objects.filter(drugagmp=drug).first()
                if variant:
                    return variant
                else:
                    # Still return something even if no variant is found
                    # This allows the view to continue and show drug info
                    return Variantagmp(drugagmp=drug)
            except Http404:
                logger.warning(f"No drug found with drug_bank_id: {rs_id}")
                raise Http404(f"No drug found with ID: {rs_id}")
            except Exception as e:
                logger.error(f"Error retrieving drug {rs_id}: {str(e)}")
                raise Http404(f"Error retrieving drug: {str(e)}")
        else:
            # For non-DB IDs - Always get the first matching variant when multiple exist
            try:
                # First try with a direct filter
                variants = Variantagmp.objects.filter(rs_id=rs_id)
                if variants.exists():
                    return variants.first()  # Return the first match if found
                else:
                    # If no variants found, raise a 404 instead of causing a 500 error
                    logger.warning(f"No variant found with rs_id: {rs_id}")
                    raise Http404(f"No variant found with rs_id: {rs_id}")
            except Variantagmp.DoesNotExist:
                # Also handle the DoesNotExist exception properly
                logger.warning(f"Variant.DoesNotExist error for rs_id: {rs_id}")
                raise Http404(f"No variant found with rs_id: {rs_id}")
            except Exception as e:
                # Catch any other unexpected errors and log them
                logger.error(f"Unexpected error for rs_id {rs_id}: {str(e)}")
                raise Http404(f"Error retrieving variant: {str(e)}")
                
    def get_context_data(self, **kwargs):
        context = super(VariantDrugAssociationDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        
        try:
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
                    ).exclude(
                        variantagmp__source_db__in=["DisGeNET", "GWAS Catalog"]
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
        except Exception as e:
            logger.error(f"Error in context data for {rs_id}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."
            
        return context

#################### Variant Var Drug Associations ################################
class VvarDrugAssocDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'VarDrugAssocDetail.html'
    pk_url_kwarg = 'rs_id'

    def get_object(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        
        # Validate rs_id format first
        if rs_id and not rs_id.startswith("DB") and not is_valid_rs_id(rs_id):
            logger.warning(f"Invalid rs_id format: {rs_id}")
            raise Http404(f"Invalid variant ID format: {rs_id}")
            
        try:
            data = Variantagmp.objects.filter(rs_id=rs_id)
            if not data.exists():
                logger.warning(f"No variant found with rs_id: {rs_id}")
                raise Http404(f"No variant found with rs_id: {rs_id}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving variant {rs_id}: {str(e)}")
            raise Http404(f"Error retrieving variant: {str(e)}")
    
    def get_context_data(self, **kwargs):
        context = super(VvarDrugAssocDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        
        try:
            context['variantagmp'] = Variantagmp.objects.filter(rs_id=rs_id)
            variant = Variantagmp.objects.filter(rs_id=rs_id)
            
            context['object_list'] = VariantStudyagmp.objects.filter(
                variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id)))
        except Exception as e:
            logger.error(f"Error in get_context_data for variant {rs_id}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."
            
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
        
        try:
            # Check if data exists for this phenotype
            variants = Variantagmp.objects.filter(phenotypeagmp__name=phenotypeagmp__name)
            if not variants.exists():
                logger.warning(f"No variants found with phenotype: {phenotypeagmp__name}")
                raise Http404(f"No variants found with phenotype: {phenotypeagmp__name}")
            # This method doesn't actually return anything, but we need to pass the check
            return variants
        except Exception as e:
            logger.error(f"Error checking phenotype {phenotypeagmp__name}: {str(e)}")
            raise Http404(f"Error retrieving phenotype data: {str(e)}")

    def get_context_data(self, **kwargs):
        context = super(DiseaseVariantDetailView, self).get_context_data(**kwargs)
        phenotypeagmp__name = self.kwargs.get(self.pk_url_kwarg)

        try:
            phenotype_data = Variantagmp.objects.filter(
                phenotypeagmp__name=phenotypeagmp__name).values("phenotypeagmp__name").distinct()
                
            if phenotype_data.exists():
                context['data'] = phenotype_data[0]
               
                context['object_list1'] = VariantStudyagmp.objects.select_related().filter(
                    variantagmp__phenotypeagmp__name__iregex=r"\\y{0}\\y".format(str(phenotypeagmp__name))
                ).exclude(variantagmp__source_db="PharmGKB")
               
                context['object_list'] = VariantStudyagmp.objects.select_related().filter(
                    variantagmp__phenotypeagmp__name__iexact=phenotypeagmp__name).exclude(variantagmp__source_db="PharmGKB")
            else:
                context['error'] = f"No data found for phenotype: {phenotypeagmp__name}"
        except Exception as e:
            logger.error(f"Error in get_context_data for phenotype {phenotypeagmp__name}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."
        
        return context
       
#################### Variant Var Drug Associations ################################
class VarDisAssocDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'VarDissAssocDetail.html'
    pk_url_kwarg = 'rs_id'

    def get_object(self):
        rs_id = self.kwargs.get(self.pk_url_kwarg)
        
        # Validate rs_id format first
        if rs_id and not rs_id.startswith("DB") and not is_valid_rs_id(rs_id):
            logger.warning(f"Invalid rs_id format: {rs_id}")
            raise Http404(f"Invalid variant ID format: {rs_id}")
            
        try:
            data = Variantagmp.objects.filter(rs_id=rs_id)
            if not data.exists():
                logger.warning(f"No variant found with rs_id: {rs_id}")
                raise Http404(f"No variant found with rs_id: {rs_id}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving variant {rs_id}: {str(e)}")
            raise Http404(f"Error retrieving variant: {str(e)}")
    
    def get_context_data(self, **kwargs):
        context = super(VarDisAssocDetailView, self).get_context_data(**kwargs)
        rs_id = self.kwargs.get(self.pk_url_kwarg)
     
        try:
            context['variantagmp'] = Variantagmp.objects.filter(rs_id=rs_id)
            variant = Variantagmp.objects.filter(rs_id=rs_id)
            
            context['object_list'] = VariantStudyagmp.objects.filter(
                variantagmp__rs_id__iregex=r"\b{0}\b".format(str(rs_id))).exclude(variantagmp__source_db="PharmGKB")
        except Exception as e:
            logger.error(f"Error in get_context_data for variant {rs_id}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."
        
        return context

# Display Phamacogenes and Disease associations
class PharmacoDrugDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'PharmacoDrugDetailView.html'
    pk_url_kwarg = 'gene_id'
    

    def get_object(self):
        gene_id = self.kwargs.get(self.pk_url_kwarg)

        try:
            data = Geneagmp.objects.filter(gene_id=gene_id)
            if not data.exists():
                logger.warning(f"No gene found with gene_id: {gene_id}")
                raise Http404(f"No gene found with gene_id: {gene_id}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving gene {gene_id}: {str(e)}")
            raise Http404(f"Error retrieving gene: {str(e)}")
    
    def get_context_data(self, **kwargs):
        context = super(PharmacoDrugDetailView, self).get_context_data(**kwargs)
        gene_id = self.kwargs.get(self.pk_url_kwarg)

        try:
            context['geneagmp'] = Geneagmp.objects.filter(
                gene_id=gene_id).first()
            
            context['object_list'] = VariantStudyagmp.objects.filter(
                variantagmp__geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id))) 
            
            context['object_list_diseases_old']=VariantStudyagmp.objects.select_related().filter(variantagmp__geneagmp__gene_id__icontains=gene_id)

            context['object_list_diseases'] = VariantStudyagmp.objects.select_related().filter(variantagmp__geneagmp__gene_id__iregex=r"\b{0}\b".format(str(gene_id))).exclude(variantagmp__source_db="PharmGKB")
        except Exception as e:
            logger.error(f"Error in get_context_data for gene {gene_id}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."
        
        return context


#################### Variant Drug Details ################################

class DrugDetailView(DetailView):
    model = VariantStudyagmp
    template_name = 'drug_detail.html'
    pk_url_kwarg = 'drug_id'

    def get_object(self):
        drug_id = self.kwargs.get(self.pk_url_kwarg)

        try:
            data = Drugagmp.objects.filter(drug_id=drug_id)
            if not data.exists():
                logger.warning(f"No drug found with drug_id: {drug_id}")
                raise Http404(f"No drug found with drug_id: {drug_id}")
            return data
        except Exception as e:
            logger.error(f"Error retrieving drug {drug_id}: {str(e)}")
            raise Http404(f"Error retrieving drug: {str(e)}")
    
    def get_context_data(self, **kwargs):
        context = super(DrugDetailView, self).get_context_data(**kwargs)
        drug_id = self.kwargs.get(self.pk_url_kwarg)
        
        try:
            context['drugagmp'] = Drugagmp.objects.filter(
                drug_id=drug_id).first()
            drug = Drugagmp.objects.filter(drug_id=drug_id).first()

            if drug:
                context['object_list'] = VariantStudyagmp.objects.filter(
                    variantagmp__drugagmp__drug_id__iregex=r"\b{0}\b".format(str(drug_id)))
                
                context['drugagmp'] = Drugagmp.objects.filter(
                   drug_id=drug.id).first()
            else:
                context['error'] = f"No drug found with ID: {drug_id}"
        except Exception as e:
            logger.error(f"Error in get_context_data for drug {drug_id}: {str(e)}")
            context['error'] = "An error occurred while retrieving data."
            
        return context

def about(request):
    return render(request, 'about.html')

def get_map_data(request, map_type):
    """Simplified map data endpoint with guaranteed timeout handling"""
    study_type = request.GET.get('study_type', 'All')
    
    try:
        # 1. Get only the data we absolutely need
        studies = VariantStudyagmp.objects.select_related('studyagmp')
        if study_type != 'All':
            studies = studies.filter(studyagmp__study_type=study_type)
        
        # 2. Load countries data just once
        countries = gpd.read_file(os.path.join(settings.BASE_DIR, 'agmp_app/static/maps/countries.geo.json'))
        
        # 3. Track publications per country
        country_counts = defaultdict(int)
        
        # 4. Process only valid coordinates (main set only - no _01, _02 etc.)
        valid_studies = studies.exclude(
            Q(latitude__isnull=True) | Q(latitude='') |
            Q(longitude__isnull=True) | Q(longitude='')
        ).values('studyagmp__publication_id', 'latitude', 'longitude')
        
        for study in valid_studies:
            try:
                point = Point(float(study['longitude']), float(study['latitude']))
                # Find which country contains this point
                for _, country in countries.iterrows():
                    if country.geometry.contains(point):
                        country_counts[country['name']] += 1
                        break
            except (ValueError, TypeError):
                continue
        
        # 5. Create the appropriate map
        if map_type == 'marker':
            m = folium.Map(location=[0, 0], zoom_start=2)
            for _, country in countries.iterrows():
                count = country_counts.get(country['name'], 0)
                if count > 0:
                    folium.Marker(
                        [country.geometry.centroid.y, country.geometry.centroid.x],
                        popup=f"{country['name']}: {count} studies"
                    ).add_to(m)
        
        elif map_type == 'heatmap':
            m = folium.Map(location=[0, 0], zoom_start=2)
            for _, country in countries.iterrows():
                count = country_counts.get(country['name'], 0)
                color = (
                    "#8B0000" if count > 100 else
                    "#CD5C5C" if count > 50 else
                    "#DAA520" if count > 10 else
                    "#F0E68C" if count > 1 else
                    "#FFFFE0"
                )
                folium.GeoJson(
                    country.geometry,
                    style_function=lambda _, c=color: {
                        'fillColor': c,
                        'color': 'black',
                        'weight': 1,
                        'fillOpacity': 0.7
                    },
                    tooltip=f"{country['name']}: {count} studies"
                ).add_to(m)
        
        return JsonResponse({'map_html': m._repr_html_()})
    
    except Exception as e:
        logger.error(f"Map generation error: {str(e)}")
        return JsonResponse({'error': 'Could not generate map'}, status=500)

def summary(request):
    """
    Main view for the summary page
    """
    try:
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
    except Exception as e:
        logger.error(f"Error in summary view: {str(e)}")
        return render(request, 'error.html', {'error': 'An error occurred while loading the summary page'})

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

def test_data_table(request):
    return render(request, 'test_data_table.html')

from django.http import JsonResponse
from collections import defaultdict
import reverse_geocoder as rg

# Local cache for lat/lon lookups
coord_cache = {}

def is_valid_coord(lat, lon):
    """
    Checks whether lat/lon are valid values (not blank, not NaN).
    """
    try:
        return (
            lat is not None
            and lon is not None
            and lat != ""
            and lon != ""
            and str(lat).lower() != "nan"
            and str(lon).lower() != "nan"
        )
    except Exception:
        return False

def reverse_geocode(lat, lon):
    """
    Reverse-geocode lat/lon to country code.
    Caches results for efficiency.
    """
    key = (round(float(lat), 4), round(float(lon), 4))
    if key in coord_cache:
        return coord_cache[key]
    
    result = rg.search(key, mode=1)[0]
    country_code = result["cc"]
    coord_cache[key] = country_code
    return country_code

def studies_per_country(request):
    """
    Returns JSON of unique publication_ids per country.
    """

    from .models import VariantStudyagmp

    variant_studies = VariantStudyagmp.objects.all()

    # Mapping: country → set of publication_ids
    country_to_publication_ids = defaultdict(set)

    for vs in variant_studies:
        for i in range(12):
            country_field = "country_participant" if i == 0 else f"country_participant_{i:02}"
            lat_field = "latitude" if i == 0 else f"latitude_{i:02}"
            lon_field = "longitude" if i == 0 else f"longitude_{i:02}"

            country_name = getattr(vs, country_field, None)
            lat = getattr(vs, lat_field, None)
            lon = getattr(vs, lon_field, None)

            # Determine country
            if country_name:
                country = country_name.strip()
            elif is_valid_coord(lat, lon):
                try:
                    country = reverse_geocode(lat, lon)
                except Exception:
                    continue
            else:
                continue

            # Ensure study exists and has a publication_id
            if (
                vs.studyagmp
                and vs.studyagmp.publication_id
                and vs.studyagmp.publication_id.strip() != ""
            ):
                pub_id = vs.studyagmp.publication_id.strip()
                country_to_publication_ids[country].add(pub_id)

    # Prepare final result: count unique publication_ids per country
    result = {
        country: len(publication_ids)
        for country, publication_ids in country_to_publication_ids.items()
    }

    return JsonResponse(result)

from django.shortcuts import render
from collections import defaultdict
import reverse_geocoder as rg

coord_cache = {}

def is_valid_coord(lat, lon):
    """
    Checks whether lat/lon are valid values (not blank, not NaN).
    """
    try:
        return (
            lat is not None
            and lon is not None
            and lat != ""
            and lon != ""
            and str(lat).lower() != "nan"
            and str(lon).lower() != "nan"
        )
    except Exception:
        return False

def reverse_geocode(lat, lon):
    """
    Reverse-geocode lat/lon to country code.
    Caches results for efficiency.
    """
    key = (round(float(lat), 4), round(float(lon), 4))
    if key in coord_cache:
        return coord_cache[key]
    
    result = rg.search(key, mode=1)[0]
    country_code = result["cc"]
    coord_cache[key] = country_code
    return country_code

def studies_per_country_view(request):
    """
    Renders HTML page showing unique publication_ids per country.
    """
    from .models import VariantStudyagmp
    from collections import defaultdict
    
    variant_studies = VariantStudyagmp.objects.select_related('studyagmp').all()
    
    # Country → set of publication_ids
    country_to_pub_ids = defaultdict(set)
    country_coords = defaultdict(lambda: {"latitudes": set(), "longitudes": set()})
    
    # Debug counters
    total_variant_studies = variant_studies.count()
    valid_publication_ids = 0
    
    for vs in variant_studies:
        for i in range(12):
            country_field = "country_participant" if i == 0 else f"country_participant_{i:02d}"
            lat_field = "latitude" if i == 0 else f"latitude_{i:02d}"
            lon_field = "longitude" if i == 0 else f"longitude_{i:02d}"
            
            country_name = getattr(vs, country_field, None)
            lat = getattr(vs, lat_field, None)
            lon = getattr(vs, lon_field, None)
            
            # Determine country
            if country_name:
                country = country_name.strip()
            elif is_valid_coord(lat, lon):
                try:
                    country = reverse_geocode(lat, lon)
                except Exception:
                    continue
            else:
                continue
            
            # Only if publication_id exists and is valid
            if (
                vs.studyagmp
                and vs.studyagmp.publication_id
                and vs.studyagmp.publication_id.strip() != ""
            ):
                pub_id = vs.studyagmp.publication_id.strip()
                country_to_pub_ids[country].add(pub_id)
                valid_publication_ids += 1
                
                # Save lat/lon for that country
                if is_valid_coord(lat, lon):
                    country_coords[country]["latitudes"].add(str(lat))
                    country_coords[country]["longitudes"].add(str(lon))
    
    # Format for template
    country_data = []
    total_unique_studies = 0
    
    for country, pub_ids in country_to_pub_ids.items():
        count = len(pub_ids)  # This is the count of UNIQUE publication_ids
        total_unique_studies += count
        
        latitudes = sorted(country_coords[country]["latitudes"])
        longitudes = sorted(country_coords[country]["longitudes"])
        
        country_data.append({
            "country": country,
            "count": count,  # Unique publication_id count per country
            "publication_ids": list(pub_ids),  # Optional: actual publication IDs
            "latitudes": latitudes,
            "longitudes": longitudes
        })
    
    # Debug info (you can remove this in production)
    print(f"Total VariantStudyagmp records: {total_variant_studies}")
    print(f"Records with valid publication_ids: {valid_publication_ids}")
    print(f"Total unique publication_ids across all countries: {total_unique_studies}")
    print(f"Countries with studies: {len(country_data)}")
    
    context = {
        "country_data": sorted(country_data, key=lambda x: x["country"]),
        "total_studies": total_unique_studies,
        "debug_info": {
            "total_variant_studies": total_variant_studies,
            "valid_publication_ids": valid_publication_ids,
            "unique_countries": len(country_data)
        }
    }
    
    return render(request, "studies_per_country.html", context)


def display_study_coordinates(request):
    studies_with_coords = []
    
    for study in Studyagmp.objects.all():
        variant_studies = VariantStudyagmp.objects.filter(studyagmp=study)
        
        coordinates = []
        for vs in variant_studies:
            # Base fields (no number)
            if vs.latitude and vs.longitude:
                coordinates.append({
                    'country': vs.country_participant,
                    'latitude': vs.latitude,
                    'longitude': vs.longitude,
                    'index': 0
                })
            
            # Numbered fields
            for i in range(1, 12):
                # Handle different numbering patterns in your model
                suffix_options = [
                    f'_{i:02d}',  # _01, _02, etc.
                    f'_{i}',       # _1, _2, etc.
                    f'_{i:03d}'    # _001, _002, etc. (though your model doesn't seem to use this)
                ]
                
                for suffix in suffix_options:
                    try:
                        lat = getattr(vs, f'latitude{suffix}')
                        lng = getattr(vs, f'longitude{suffix}')
                        country = getattr(vs, f'country_participant{suffix}')
                        
                        if lat and lng:
                            coordinates.append({
                                'country': country,
                                'latitude': lat,
                                'longitude': lng,
                                'index': i
                            })
                            break  # Found the right suffix, move to next i
                    except AttributeError:
                        continue
        
        if coordinates:
            studies_with_coords.append({
                'study': study,
                'coordinates': coordinates
            })
    
    return render(request, 'study_coordinates.html', {'studies': studies_with_coords})