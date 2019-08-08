from django.shortcuts import render, HttpResponse
from django.core import serializers
from itertools import chain

from .models import  pharmacogenes, drug, snp, star_allele, study
from .forms import PostForm
import json

def index(request):
    return render(request, 'index.html')

def about(request):
    return render(request, 'about.html')

def search(request):
    form = PostForm(
        initial = {
            'gene_name': '',
            'protein': '',
            'function': ''
        }
    )
    return render(request, 'search.html', {"form": form})

def search_details(request, db_name, search_type, query_id):
    '''
    Receive query parameters from search page to fetch
    database specific results
    '''
    drug_list = None
    gene_list = None
    variant_list = None
    disease_list = None

    # query incoming request based on a drug
    if (search_type == 'dg'):
        drug_list = drug.objects.filter(drug_id__exact= query_id).values()
    if (search_type == 'ge'):
        gene_list = pharmacogenes.objects.filter(drug_id__exact= query_id).values()
    if (search_type == 'vt'):
        variant_list = snp.objects.filter(drug_id__exact= query_id).values()
    if (search_type == 'ds'):
        disease_list = disease.objects.filter(drug_id__exact= query_id).values()

    return render(
        request, 'search_details.html', {
            'db_name': db_name,
            'search_type': search_type,
            'query_id': query_id,
            'drug': drug_list,
            'gene': gene_list,
            'variant': variant_list,
            'disease': disease_list,
            }
        )

def __fetch_disease(diseases):
    '''
    :param list item_list: a list of item names to fetch from disease table
    :return dict
    '''
    ret = []
    for disease in diseases:
        disease_object = dict()
        disease_object['key'] = 'ds'
        disease_object['result_type'] = 'disease'
        disease_object['name'] = disease['drug_name']
        disease_object['posology'] = disease['posology']
        disease_object['chemical_structure'] = disease['chemical_structure']
        ret.append(disease_object)
    print('DISEASE ',ret)
    return ret

def __fetch_drug(drugs):
    '''
    :param list item_list: a list of item names to fetch from drug table
    :return dict
    '''
    ret = []
    # drugs = drug.objects.filter(drug_name__contains= query).values()
    for drug in drugs:
        drug_object = dict()
        drug_object['key'] = 'dg'
        drug_object['result_type'] = 'drug'

        drug_object['name'] = drug['drug_name']
        drug_object['posology'] = drug['posology']
        drug_object['chemical_structure'] = drug['chemical_structure']
        ret.append(drug_object)
    print('DRUG ',ret)
    return ret

def __fetch_variant(snps):
    '''
    :param list item_list: a list of item names to fetch from snp table
    :return dict
    '''
    ret = []

    for snp in snps:
        variant_object = dict()
        variant_object['key'] = 'vt'
        variant_object['result_type'] = 'variant'

        variant_object['name'] = snp['rs_id']
        variant_object['drug'] = snp['drug_id']
        variant_object['allele'] = snp['allele']
        variant_object['gene'] = snp['gene_id']
        variant_object['disease_phenotype'] = snp['disease_phenotype']
        variant_object['reference'] = snp['reference_id']
        variant_object['chromosome'] = snp['chromosome']
        variant_object['p_value'] = float(snp['p_value'])
        ret.append(variant_object)
    print('VARIANT ',ret)
    return ret

def __fetch_gene(genes):
    '''
    :param list item_list: a list of item names to fetch from study table
    :return dict
    '''
    ret = []
    # genes = pharmacogenes.objects.filter(gene_name__contains= query).values()
    for gene in genes:
        gene_object = dict()
        gene_object['key'] = 'ge'
        gene_object['result_type'] = 'gene'

        gene_object['name'] = gene['gene_name']
        gene_object['protein'] = gene['protein']
        gene_object['function'] = gene['function']
        ret.append(gene_object)
    print('GENE ',ret)
    return ret

def __fetch_data(model, item_list):
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
    is_variant =  int(request.GET.get('variant', 0))
    is_gene = int(request.GET.get('gene', 0))

    pass_list = []

    if request.is_ajax():
        # TODO: there must be a better way to do this
        if is_disease:
            pass_list += __fetch_disease(star_allele.objects.filter(disease_phenotype__contains= query_string).values())
        
        if is_drug:
            pass_list += __fetch_drug(drug.objects.filter(drug_name__contains= query_string).values())
        
        if is_variant:
            pass_list += __fetch_variant(snp.objects.filter(rs_id__exact= query_string).values())
        if is_gene:
            pass_list += __fetch_gene(pharmacogenes.objects.filter(gene_name__contains= query_string).values())

    res = json.dumps(pass_list)
    mimetype = 'application/json'

    return HttpResponse(res, mimetype)

def summary(request):
    return render(request, 'summary.html')

def resources(request):
    return render(request, 'resources.html')

def outreach(request):
    return render(request, 'outreach.html')

def contact(request):
    return render(request, 'contact.html')

