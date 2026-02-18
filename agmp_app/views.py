import logging
import re
from urllib.parse import DefragResult
from django.shortcuts import render, HttpResponse, redirect, get_object_or_404
from django.http import FileResponse, JsonResponse, Http404, HttpResponse
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

from django.views.decorators.http import require_http_methods

import csv
import io

# ============================================================ # ============================================================
import json
import csv
import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, Variantagmp, VariantStudyagmp

logger = logging.getLogger(__name__)


import json
import csv
import logging
from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.db.models import Q
from .models import Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, Variantagmp, VariantStudyagmp

logger = logging.getLogger(__name__)


def batch_query_view(request):
    return render(request, 'batch_query.html')


def batch_query_execute(request):
    if request.method != 'POST':
        return JsonResponse({'success': False, 'error': 'POST required'})
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'success': False, 'error': 'Invalid JSON'})
    
    query_type = data.get('query_type', '')
    queries = data.get('queries', [])
    output_fields = data.get('output_fields', [])
    
    if not query_type:
        return JsonResponse({'success': False, 'error': 'Select a query type'})
    if not queries:
        return JsonResponse({'success': False, 'error': 'Provide at least one search term'})
    if not output_fields:
        return JsonResponse({'success': False, 'error': 'Select at least one output field'})
    
    seen = set()
    unique_queries = []
    for q in queries:
        q = q.strip()
        if q and q.lower() not in seen:
            seen.add(q.lower())
            unique_queries.append(q)
    
    queries = unique_queries[:1000]
    results = []
    not_found = []
    
    for query in queries:
        if query_type == 'variant':
            row = query_variant_data(query, output_fields)
        elif query_type == 'gene':
            row = query_gene_data(query, output_fields)
        elif query_type == 'drug':
            row = query_drug_data(query, output_fields)
        elif query_type == 'phenotype':
            row = query_phenotype_data(query, output_fields)
        else:
            row = None
        
        if row:
            row['_input'] = query
            row['_status'] = 'found'
            results.append(row)
        else:
            results.append({'_input': query, '_status': 'not_found'})
            not_found.append(query)
    
    return JsonResponse({
        'success': True,
        'results': results,
        'total': len(results),
        'found': len(results) - len(not_found),
        'not_found_count': len(not_found),
        'not_found_list': not_found
    })


def query_variant_data(rs_id, fields):
    """Query variant with full related details."""
    try:
        variant = Variantagmp.objects.filter(
            Q(rs_id__iexact=rs_id) | Q(rs_id__icontains=rs_id)
        ).select_related('geneagmp', 'drugagmp', 'phenotypeagmp').first()
        
        if not variant:
            return None
        
        result = {}
        
        # Main variant fields
        if 'rs_id' in fields:
            result['rs_id'] = variant.rs_id or ''
        if 'variant_type' in fields:
            result['variant_type'] = variant.variant_type or ''
        if 'allele' in fields:
            result['allele'] = variant.allele or ''
        if 'source_db' in fields:
            result['source_db'] = variant.source_db or ''
        if 'gene_name' in fields:
            result['gene_name'] = variant.geneagmp.gene_name if variant.geneagmp else ''
        if 'chromosome' in fields:
            result['chromosome'] = variant.geneagmp.chromosome if variant.geneagmp else ''
        
        # Gene detail fields
        if 'gene_id' in fields:
            result['gene_id'] = variant.geneagmp.gene_id if variant.geneagmp else ''
        if 'gene_function' in fields:
            result['gene_function'] = variant.geneagmp.function if variant.geneagmp else ''
        if 'uniprot_ac' in fields:
            result['uniprot_ac'] = variant.geneagmp.uniprot_ac if variant.geneagmp else ''
        
        # Get all variant entries with same rs_id for comprehensive data
        all_variants = Variantagmp.objects.filter(
            rs_id__iexact=rs_id
        ).select_related('drugagmp', 'phenotypeagmp')
        
        # Drugs detail
        if 'drugs_detail' in fields:
            drugs = []
            seen_drugs = set()
            for v in all_variants:
                if v.drugagmp and v.drugagmp.drug_bank_id not in seen_drugs:
                    seen_drugs.add(v.drugagmp.drug_bank_id)
                    drugs.append({
                        'name': v.drugagmp.drug_name or '',
                        'drug_bank_id': v.drugagmp.drug_bank_id or '',
                        'indication': (v.drugagmp.indication or '')[:100]
                    })
            result['drugs_detail'] = drugs[:30]
        
        # Phenotypes detail
        if 'phenotypes_detail' in fields:
            phenotypes = []
            seen_pheno = set()
            for v in all_variants:
                if v.phenotypeagmp and v.phenotypeagmp.name not in seen_pheno:
                    seen_pheno.add(v.phenotypeagmp.name)
                    phenotypes.append({'name': v.phenotypeagmp.name})
            result['phenotypes_detail'] = phenotypes[:50]
        
        # Studies detail
        if 'studies_detail' in fields or 'countries_detail' in fields:
            variant_studies = VariantStudyagmp.objects.filter(
                variantagmp__rs_id__iexact=rs_id
            ).select_related('studyagmp')
            
            if 'studies_detail' in fields:
                studies = []
                seen_studies = set()
                for vs in variant_studies:
                    if vs.studyagmp and vs.studyagmp.publication_id not in seen_studies:
                        seen_studies.add(vs.studyagmp.publication_id)
                        studies.append({
                            'title': (vs.studyagmp.title or '')[:150],
                            'pubmed_id': vs.studyagmp.publication_id or '',
                            'year': vs.studyagmp.publication_year or '',
                            'study_type': vs.studyagmp.study_type or ''
                        })
                result['studies_detail'] = studies[:20]
            
            if 'countries_detail' in fields:
                countries = []
                for vs in variant_studies[:10]:
                    country_data = extract_countries(vs)
                    countries.extend(country_data)
                result['countries_detail'] = countries[:30]
        
        # Counts
        if 'drug_assoc_count' in fields:
            result['drug_assoc_count'] = all_variants.exclude(
                source_db__in=["DisGeNET", "GWAS Catalog"]
            ).exclude(drugagmp__isnull=True).count()
        if 'phenotype_assoc_count' in fields:
            result['phenotype_assoc_count'] = all_variants.filter(
                source_db__in=["DisGeNET", "GWAS Catalog"]
            ).exclude(phenotypeagmp__isnull=True).count()
        if 'study_count' in fields:
            result['study_count'] = VariantStudyagmp.objects.filter(
                variantagmp__rs_id__iexact=rs_id
            ).values('studyagmp__publication_id').distinct().count()
        
        return result
    except Exception as e:
        logger.error(f"query_variant_data error: {str(e)}")
        return None


def query_gene_data(gene_input, fields):
    """Query gene with full related details."""
    try:
        gene = Geneagmp.objects.filter(
            Q(gene_id__iexact=gene_input) | Q(gene_name__iexact=gene_input)
        ).first()
        
        if not gene:
            return None
        
        result = {}
        
        # Main gene fields
        if 'gene_id' in fields:
            result['gene_id'] = gene.gene_id or ''
        if 'gene_name' in fields:
            result['gene_name'] = gene.gene_name or ''
        if 'chromosome' in fields:
            result['chromosome'] = gene.chromosome or ''
        if 'function' in fields:
            result['function'] = gene.function or ''
        if 'uniprot_ac' in fields:
            result['uniprot_ac'] = gene.uniprot_ac or ''
        
        variants = Variantagmp.objects.filter(geneagmp=gene).select_related('drugagmp', 'phenotypeagmp')
        
        # Variants detail
        if 'variants_detail' in fields:
            var_list = []
            seen = set()
            for v in variants:
                if v.rs_id and v.rs_id not in seen:
                    seen.add(v.rs_id)
                    var_list.append({
                        'id': v.rs_id,
                        'type': v.variant_type or '',
                        'allele': v.allele or ''
                    })
            result['variants_detail'] = var_list[:50]
        
        # Drugs detail
        if 'drugs_detail' in fields:
            drugs = []
            seen = set()
            for v in variants:
                if v.drugagmp and v.drugagmp.drug_bank_id not in seen:
                    seen.add(v.drugagmp.drug_bank_id)
                    drugs.append({
                        'name': v.drugagmp.drug_name or '',
                        'drug_bank_id': v.drugagmp.drug_bank_id or '',
                        'state': v.drugagmp.state or ''
                    })
            result['drugs_detail'] = drugs[:30]
        
        # Phenotypes detail
        if 'phenotypes_detail' in fields:
            phenos = []
            seen = set()
            for v in variants:
                if v.phenotypeagmp and v.phenotypeagmp.name not in seen:
                    seen.add(v.phenotypeagmp.name)
                    phenos.append({'name': v.phenotypeagmp.name})
            result['phenotypes_detail'] = phenos[:50]
        
        # Studies detail
        if 'studies_detail' in fields or 'countries_detail' in fields:
            variant_studies = VariantStudyagmp.objects.filter(
                variantagmp__geneagmp=gene
            ).select_related('studyagmp')
            
            if 'studies_detail' in fields:
                studies = []
                seen = set()
                for vs in variant_studies:
                    if vs.studyagmp and vs.studyagmp.publication_id not in seen:
                        seen.add(vs.studyagmp.publication_id)
                        studies.append({
                            'title': (vs.studyagmp.title or '')[:150],
                            'pubmed_id': vs.studyagmp.publication_id or '',
                            'year': vs.studyagmp.publication_year or '',
                            'study_type': vs.studyagmp.study_type or ''
                        })
                result['studies_detail'] = studies[:20]
            
            if 'countries_detail' in fields:
                countries = []
                for vs in variant_studies[:15]:
                    countries.extend(extract_countries(vs))
                # Deduplicate countries
                seen = set()
                unique_countries = []
                for c in countries:
                    if c['country'] not in seen:
                        seen.add(c['country'])
                        unique_countries.append(c)
                result['countries_detail'] = unique_countries[:30]
        
        # Counts
        if 'variant_count' in fields:
            result['variant_count'] = variants.values('rs_id').distinct().count()
        if 'drug_assoc_count' in fields:
            result['drug_assoc_count'] = variants.exclude(drugagmp__isnull=True).count()
        if 'phenotype_assoc_count' in fields:
            result['phenotype_assoc_count'] = variants.exclude(phenotypeagmp__isnull=True).count()
        if 'study_count' in fields:
            result['study_count'] = VariantStudyagmp.objects.filter(
                variantagmp__geneagmp=gene
            ).values('studyagmp__publication_id').distinct().count()
        
        return result
    except Exception as e:
        logger.error(f"query_gene_data error: {str(e)}")
        return None


def query_drug_data(drug_input, fields):
    """Query drug with full related details."""
    try:
        drug = Drugagmp.objects.filter(
            Q(drug_name__iexact=drug_input) | Q(drug_bank_id__iexact=drug_input)
        ).first()
        
        if not drug:
            return None
        
        result = {}
        
        # Main drug fields
        if 'drug_name' in fields:
            result['drug_name'] = drug.drug_name or ''
        if 'drug_bank_id' in fields:
            result['drug_bank_id'] = drug.drug_bank_id or ''
        if 'drug_id' in fields:
            result['drug_id'] = drug.drug_id or ''
        if 'state' in fields:
            result['state'] = drug.state or ''
        if 'indication' in fields:
            result['indication'] = drug.indication or ''
        if 'iupac_name' in fields:
            result['iupac_name'] = drug.iupac_name_seq or ''
        
        variants = Variantagmp.objects.filter(drugagmp=drug).select_related('geneagmp', 'phenotypeagmp')
        
        # Genes detail
        if 'genes_detail' in fields:
            genes = []
            seen = set()
            for v in variants:
                if v.geneagmp and v.geneagmp.gene_id not in seen:
                    seen.add(v.geneagmp.gene_id)
                    genes.append({
                        'id': v.geneagmp.gene_id or '',
                        'name': v.geneagmp.gene_name or '',
                        'chromosome': v.geneagmp.chromosome or '',
                        'function': (v.geneagmp.function or '')[:100]
                    })
            result['genes_detail'] = genes[:30]
        
        # Variants detail
        if 'variants_detail' in fields:
            vars_list = []
            seen = set()
            for v in variants:
                if v.rs_id and v.rs_id not in seen:
                    seen.add(v.rs_id)
                    vars_list.append({
                        'id': v.rs_id,
                        'type': v.variant_type or '',
                        'gene': v.geneagmp.gene_name if v.geneagmp else ''
                    })
            result['variants_detail'] = vars_list[:50]
        
        # Phenotypes detail
        if 'phenotypes_detail' in fields:
            phenos = []
            seen = set()
            for v in variants:
                if v.phenotypeagmp and v.phenotypeagmp.name not in seen:
                    seen.add(v.phenotypeagmp.name)
                    phenos.append({'name': v.phenotypeagmp.name})
            result['phenotypes_detail'] = phenos[:50]
        
        # Studies detail
        if 'studies_detail' in fields:
            variant_studies = VariantStudyagmp.objects.filter(
                variantagmp__drugagmp=drug
            ).select_related('studyagmp')
            studies = []
            seen = set()
            for vs in variant_studies:
                if vs.studyagmp and vs.studyagmp.publication_id not in seen:
                    seen.add(vs.studyagmp.publication_id)
                    studies.append({
                        'title': (vs.studyagmp.title or '')[:150],
                        'pubmed_id': vs.studyagmp.publication_id or '',
                        'year': vs.studyagmp.publication_year or '',
                        'study_type': vs.studyagmp.study_type or ''
                    })
            result['studies_detail'] = studies[:20]
        
        # Counts
        if 'variant_count' in fields:
            result['variant_count'] = variants.values('rs_id').distinct().count()
        if 'gene_count' in fields:
            result['gene_count'] = variants.values('geneagmp__gene_id').distinct().count()
        if 'study_count' in fields:
            result['study_count'] = VariantStudyagmp.objects.filter(
                variantagmp__drugagmp=drug
            ).values('studyagmp__publication_id').distinct().count()
        
        return result
    except Exception as e:
        logger.error(f"query_drug_data error: {str(e)}")
        return None


def query_phenotype_data(phenotype_name, fields):
    """Query phenotype with full related details."""
    try:
        variants = Variantagmp.objects.filter(
            phenotypeagmp__name__iexact=phenotype_name
        ).select_related('geneagmp', 'drugagmp', 'phenotypeagmp')
        
        if not variants.exists():
            return None
        
        result = {}
        
        if 'phenotype_name' in fields:
            result['phenotype_name'] = phenotype_name
        
        # Genes detail
        if 'genes_detail' in fields:
            genes = []
            seen = set()
            for v in variants:
                if v.geneagmp and v.geneagmp.gene_id not in seen:
                    seen.add(v.geneagmp.gene_id)
                    genes.append({
                        'id': v.geneagmp.gene_id or '',
                        'name': v.geneagmp.gene_name or '',
                        'chromosome': v.geneagmp.chromosome or ''
                    })
            result['genes_detail'] = genes[:30]
        
        # Variants detail
        if 'variants_detail' in fields:
            vars_list = []
            seen = set()
            for v in variants:
                if v.rs_id and v.rs_id not in seen:
                    seen.add(v.rs_id)
                    vars_list.append({
                        'id': v.rs_id,
                        'gene': v.geneagmp.gene_name if v.geneagmp else ''
                    })
            result['variants_detail'] = vars_list[:50]
        
        # Drugs detail
        if 'drugs_detail' in fields:
            drugs = []
            seen = set()
            for v in variants:
                if v.drugagmp and v.drugagmp.drug_bank_id not in seen:
                    seen.add(v.drugagmp.drug_bank_id)
                    drugs.append({
                        'name': v.drugagmp.drug_name or '',
                        'drug_bank_id': v.drugagmp.drug_bank_id or ''
                    })
            result['drugs_detail'] = drugs[:30]
        
        # Studies detail
        if 'studies_detail' in fields:
            variant_studies = VariantStudyagmp.objects.filter(
                variantagmp__phenotypeagmp__name__iexact=phenotype_name
            ).select_related('studyagmp')
            studies = []
            seen = set()
            for vs in variant_studies:
                if vs.studyagmp and vs.studyagmp.publication_id not in seen:
                    seen.add(vs.studyagmp.publication_id)
                    studies.append({
                        'title': (vs.studyagmp.title or '')[:150],
                        'pubmed_id': vs.studyagmp.publication_id or '',
                        'year': vs.studyagmp.publication_year or '',
                        'study_type': vs.studyagmp.study_type or ''
                    })
            result['studies_detail'] = studies[:20]
        
        # Counts
        if 'variant_count' in fields:
            result['variant_count'] = variants.values('rs_id').distinct().count()
        if 'gene_count' in fields:
            result['gene_count'] = variants.values('geneagmp__gene_id').distinct().count()
        if 'study_count' in fields:
            result['study_count'] = VariantStudyagmp.objects.filter(
                variantagmp__phenotypeagmp__name__iexact=phenotype_name
            ).values('studyagmp__publication_id').distinct().count()
        
        return result
    except Exception as e:
        logger.error(f"query_phenotype_data error: {str(e)}")
        return None


def extract_countries(variant_study):
    """Extract all country data from a VariantStudyagmp record."""
    countries = []
    
    # Main country
    if variant_study.country_participant:
        countries.append({
            'country': variant_study.country_participant,
            'lat': variant_study.latitude,
            'lng': variant_study.longitude
        })
    
    # Additional countries (01-30)
    for i in range(1, 31):
        suffix = f'_{i:02d}' if i < 20 else f'_{i}'
        if i == 10:
            suffix = '_010'
        elif i == 11:
            suffix = '_011'
        elif i == 12:
            suffix = '_012'
        elif i == 13:
            suffix = '_013'
        elif i == 14:
            suffix = '_014'
        elif i == 15:
            suffix = '_015'
        elif i == 16:
            suffix = '_016'
        elif i == 17:
            suffix = '_017'
        elif i == 18:
            suffix = '_018'
        elif i == 19:
            suffix = '_019'
        
        country_field = f'country_participant{suffix}'
        lat_field = f'latitude{suffix}'
        lng_field = f'longitude{suffix}'
        
        country = getattr(variant_study, country_field, None)
        if country:
            countries.append({
                'country': country,
                'lat': getattr(variant_study, lat_field, None),
                'lng': getattr(variant_study, lng_field, None)
            })
    
    return countries


def batch_query_export(request):
    """Export results as CSV."""
    if request.method != 'POST':
        return HttpResponse("POST required", status=405)
    
    try:
        data = json.loads(request.body)
        results = data.get('results', [])
        columns = data.get('columns', [])
    except json.JSONDecodeError:
        return HttpResponse("Invalid data", status=400)
    
    if not results:
        return HttpResponse("No results", status=400)
    
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="batch_query_results.csv"'
    
    if not columns:
        columns = list(results[0].keys())
    
    writer = csv.writer(response)
    writer.writerow(columns)
    
    for row in results:
        csv_row = []
        for col in columns:
            val = row.get(col, '')
            if isinstance(val, list):
                # Flatten list of dicts for CSV
                val = '; '.join([
                    ' | '.join(str(v) for v in item.values()) if isinstance(item, dict) else str(item)
                    for item in val
                ])
            csv_row.append(val)
        writer.writerow(csv_row)
    
    return response

# ============================================================ # ============================================================

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
    """
    AJAX endpoint for getting map data based on study type filter
    """
    study_type = request.GET.get('study_type', 'All')
    
    try:
        
        def get_filtered_studies(study_type):
            studies = VariantStudyagmp.objects.select_related('studyagmp').distinct('studyagmp__publication_id')
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
    except Exception as e:
        logger.error(f"Error generating map data: {str(e)}")
        return JsonResponse({'error': 'An error occurred while generating map data'}, status=500)
    

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







