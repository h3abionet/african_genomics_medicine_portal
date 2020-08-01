from django.shortcuts import render, HttpResponse
from django.http import FileResponse

from django.core import serializers
from itertools import chain

from .models import disease, pharmacogenes, drug, snp as SnpModel, star_allele, study
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
            # 'protein': '',
            'function': ''
        }
    )
    return render(request, 'search.html', {"form": form})

def _get_gene_page(query):
    genes = pharmacogenes.objects.filter(id__exact= query).values()
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

    print (variant_drug)
    print (gene_list)
    print (gene_drug)
    print (disease_list)
    print (gene_details)

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
    print('DISEASE ',ret)
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
    snps = SnpModel.objects.select_related('gene').filter(rs_id__icontains= qs).all()
    print(snps)
    for snp in snps:
        # snp = snp.values()
        variant_object = dict()
        variant_object['key'] = 'vt'
        variant_object['detail'] = ["<b>Chromosome</b> {0}".format(snp.gene.chromosome_patch), "<b>Gene: {0}</b>".format(snp.gene.gene_name)]

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
        gene_object['detail'] = ['Chromosome {0}'.format(gene.get('chromosome_patch'))]

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
    is_variant =  int(request.GET.get('variant', 0))
    is_gene = int(request.GET.get('gene', 0))

    pass_list = []

    if request.is_ajax():
        # TODO: there must be a better way to do this
        if is_disease:
            disgenet_snps = SnpModel.objects.filter(source__icontains= 'DisGeNET')
            disgenet_snps = disgenet_snps.filter(association_with__icontains=query_string)
            # pass_list += _fetch_disease(disgenet_snps.values())
            pass_list += _fetch_disease(disease.objects.filter(disease_name__contains= query_string).values())
            print (pass_list)
        if is_drug:
            pass_list += _fetch_drug(drug.objects.filter(drug_name__contains= query_string).values())
        if is_variant:
            pass_list += _fetch_variant(query_string)
        if is_gene:
            pass_list += _fetch_gene(pharmacogenes.objects.filter(gene_name__contains= query_string).values())

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
    dsc = star_allele.objects.count()
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
    return render(request, 'databases.html')

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