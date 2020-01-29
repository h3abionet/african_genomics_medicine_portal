from django.shortcuts import render, HttpResponse
from django.core import serializers
from itertools import chain

from .models import  pharmacogenes, drug, snp as SnpModel, star_allele, study, snp_ethnicity_country as Country
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

def search_details(request, search_type, query_id):
    '''
    Receive query parameters from search page to fetch
    database specific results
    '''
    variant_drug = []
    gene_list = None
    gene_drug = []
    disease_list = None
    # query incoming request based on a drug
    if search_type == 'gene-drug' and query_id[0] == 'D':
        for p in pharmacogenes.objects.raw(" SELECT agmp_app_snp.id, agmp_app_snp.rs_id, external_id, p_value, region, gene_name, drug_name FROM agmp_app_snp \
 inner join agmp_app_snp_ethnicity_country on agmp_app_snp_ethnicity_country.snp = agmp_app_snp.snp_id \
 INNER JOIN agmp_app_drug on agmp_app_drug.id = agmp_app_snp.drug_id \
 INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id \
 INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id \
 AND agmp_app_snp.drug_id =%s;", [query_id]):
            gene_drug.append(p)

    if (search_type == 'variant-drug'):
        for p in pharmacogenes.objects.raw(" SELECT agmp_app_snp.id, agmp_app_snp.rs_id, external_id, p_value, region, gene_name, drug_name FROM agmp_app_snp \
 inner join agmp_app_snp_ethnicity_country on agmp_app_snp_ethnicity_country.snp = agmp_app_snp.snp_id \
 INNER JOIN agmp_app_drug on agmp_app_drug.id = agmp_app_snp.drug_id \
 INNER JOIN agmp_app_pharmacogenes on agmp_app_pharmacogenes.id = agmp_app_snp.gene_id \
 INNER JOIN agmp_app_study on agmp_app_study.id = agmp_app_snp.reference_id \
 AND agmp_app_snp.snp_id =%s;", [query_id]):
            variant_drug.append(p)

    print (variant_drug)
    print (gene_list)
    print (gene_drug)
    print (disease_list)

    return render(
        request, 'search_details.html', {
            # 'db_name': db_name,
            'search_type': search_type,
            'query_id': query_id,
            'variant_drug': variant_drug,
            'genes': gene_list,
            'gene_drug': gene_drug,
            'diseases': disease_list,
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

        disease_object['id'] = disease['id']
        disease_object['name'] = disease['star_annotation']
        disease_object['star_id'] = disease['star_id']
        disease_object['allele'] = disease['allele']
        disease_object['phenotype'] = disease['phenotype']
        disease_object['drug'] = disease['drug_id']
        disease_object['reference'] = disease['reference_id']
        disease_object['gene_id'] = disease['gene_id']
        disease_object['p_value'] = disease['p_value']
        disease_object['source'] = disease['source']
        disease_object['id_in_source'] = disease['id_in_source']
        disease_object['chromosome'] = disease['chromosome']
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
        drug_object['detail'] = [
            'Drug Bank ID: {0}'.format(drug.get('drug_bank_id')),
            'State: {0}'.format(drug.get('state'))]

        drug_object['id'] = drug['id']
        drug_object['name'] = drug['drug_name']
        drug_object['drug_bank_id'] = drug['drug_bank_id']
        drug_object['state'] = drug['state']
        drug_object['indication'] = drug['indication']
        drug_object['iupac_name'] = drug['iupac_name']
        ret.append(drug_object)
    print('DRUG ',ret)
    return ret

def __fetch_variant(qs):
    '''
    :param list item_list: a list of item names to fetch from snp table
    :return dict
    '''
    ret = []
    snps = SnpModel.objects.filter(rs_id__exact= qs).values()

    for snp in snps:
        variant_object = dict()
        variant_object['key'] = 'vt'
        variant_object['detail'] = ['Chromosome {0}'.format(snp.get('chromosome'))]

        variant_object['id'] = snp['snp_id']
        variant_object['name'] = 'RSID: {0}'.format(snp.get('rs_id'))
        variant_object['drug'] = snp['drug_id']
        variant_object['allele'] = snp['allele']
        variant_object['gene'] = snp['gene_id']
        variant_object['phenotype'] = snp['phenotype']
        variant_object['reference'] = snp['reference_id']
        variant_object['p_value'] = snp['p_value']
        variant_object['source'] = snp['source']
        variant_object['id_in_source'] = snp['id_in_source']
        variant_object['chromosome'] = snp['chromosome']
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
        gene_object['detail'] = ['Chromosome {0}'.format(gene.get('chromosome'))]

        gene_object['id'] = gene['id']
        gene_object['name'] = gene['gene_name']
        gene_object['protein'] = gene['protein']
        gene_object['function'] = gene['function']
        gene_object['chromosome'] = gene['chromosome']
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
        # if is_disease:
        #     pass_list += __fetch_disease(star_allele.objects.filter(phenotype__contains= query_string).values())
        
        if is_drug:
            pass_list += __fetch_drug(drug.objects.filter(drug_name__contains= query_string).values())
        if is_variant:
            pass_list += __fetch_variant(query_string)
        if is_gene:
            pass_list += __fetch_gene(pharmacogenes.objects.filter(gene_name__contains= query_string).values())

    res = json.dumps(pass_list)
    mimetype = 'application/json'
    return HttpResponse(res, mimetype)

def summary(request):
    '''
    :return JSON of table counts

    Returns the counts of records for the major models;
    drug, variant, disease, gene,
    '''
    dgc = drug.objects.count()
    # dsc = star_allele.objects.count
    dsc = None # nothing for disease, for now
    vtc = SnpModel.objects.count()
    gec = pharmacogenes.objects.count()
    return render(request, 'summary.html', {
        'drug_count': dgc, 
        'disease_count': dsc, 
        'variant_count': vtc,
        'gene_count': gec,
        'records': [{'LAT': 1.000, 'LON':-1.000, }]
        })

def country_summary(request):
    '''
    :return JSON of country summary
    '''
    res = []

    for p in Country.objects.raw("SELECT DISTINCT id, country_of_participants, latitude, longitude, region, snp, \
        COUNT(country_of_participants) AS cnt FROM agmp_app_snp_ethnicity_country GROUP BY country_of_participants ORDER BY cnt;"):
        res.append({
            'country': p.country_of_participants,
            'region': p.region,
            'latitude': '{:,.7f}'.format(p.latitude),
            'longitude': '{0}'.format(p.longitude),
            'snp': p.snp,
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

