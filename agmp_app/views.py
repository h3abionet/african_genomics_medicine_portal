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

def search_details(request, db_name, query_id):
    '''
    Receive query parameters from search page to fetch
    database specific results
    '''
    return render(
        request, 'search_details.html', {
            'db_name': db_name,
            'query_id': query_id
            }
        )

def fetch_disease(diseases):
    '''
    :param list item_list: a list of item names to fetch from disease table
    :return dict
    '''
    ret = []
    disease_object = dict()
    for disease in diseases:
        disease_object['result_type'] = 'disease'
        disease_object['name'] = disease['drug_name']
        disease_object['posology'] = disease['posology']
        disease_object['chemical_structure'] = disease['chemical_structure']
        ret.append(disease_object)
    print('DISEASE ',ret)
    return ret

def fetch_drug(drugs):
    '''
    :param list item_list: a list of item names to fetch from drug table
    :return dict
    '''
    ret = []
    drug_object = dict()
    # drugs = drug.objects.filter(drug_name__contains= query).values()
    for drug in drugs:
        drug_object['result_type'] = 'drug'
        drug_object['name'] = drug['drug_name']
        drug_object['posology'] = drug['posology']
        drug_object['chemical_structure'] = drug['chemical_structure']
        ret.append(drug_object)
    print('DRUG ',ret)
    return ret

def __fetch_study(studies):
    '''
    :param list item_list: a list of item names to fetch from study table
    :return dict
    '''
    ret = []
    study_object = dict()
    
    # studies = study.objects.filter(study_title__contains= query).values()
    for study in studies:
        study_object['result_type'] = 'study'
        study_object['name'] = study['study_title']
        study_object['date'] = study['date']
        ret.append(study_object)
    print('STUDY ',ret)
    return ret

def __fetch_pharmacogenes(genes):
    '''
    :param list item_list: a list of item names to fetch from study table
    :return dict
    '''
    ret = []
    gene_object = dict()
    
    # genes = pharmacogenes.objects.filter(gene_name__contains= query).values()
    for gene in genes:
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
            pass_list += fetch_disease(star_allele.objects.filter(disease_phenotype__contains= query_string).values())
        
        if is_drug:
            pass_list += fetch_drug(drug.objects.filter(drug_name__contains= query_string).values())
        
        if is_variant:
            pass_list += __fetch_study(study.objects.filter(study_title__contains= query_string).values())
        
        if is_gene:
            pass_list += __fetch_pharmacogenes(pharmacogenes.objects.filter(gene_name__contains= query_string).values())

    res = json.dumps(pass_list)
    mimetype = 'application/json'

    return HttpResponse(res, mimetype)

def resources(request):
    return render(request, 'resources.html')

def outreach(request):
    return render(request, 'outreach.html')

def contact(request):
    return render(request, 'contact.html')
