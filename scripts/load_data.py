import csv
import numpy as np
import pandas as pd
from agmp_app.models import Variantagmp, Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, VariantStudyagmp
# python3 manage.py runscript load_data
# g is for Gene
# d is for Drug
# v is for Variant
# s is for Study
# p is for Phenotype

 ################### April May 2024 ####################################
import pandas as pd
from agmp_app.models import Variantagmp, Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, VariantStudyagmp

def run():

    # Delete all models
    Variantagmp.objects.all().delete()
    Drugagmp.objects.all().delete()
    Geneagmp.objects.all().delete()
    Studyagmp.objects.all().delete()
    Phenotypeagmp.objects.all().delete()
    VariantStudyagmp.objects.all().delete()

    # Import the first file
    df_csv = pd.read_csv('import_csv/first_import_job_run_error_fix.csv', encoding='latin-1')
    # replaces NS and nan with NR
    def normalize_01_p_value(value):
        if pd.isna(value) or value in ['NS', 'nan']:
            return 'NR'
        return value



    for index, row in df_csv.iterrows():
        print(row)
        p, created = Phenotypeagmp.objects.get_or_create(name=row['phenotype'])
        s, created = Studyagmp.objects.get_or_create(data_ac=row['data_ac'], publication_id=row['publication'], publication_year=row['publication_year'], study_type=row['study_type'], title=row['title'])
        d, created = Drugagmp.objects.get_or_create(drug_bank_id=row['ID Drug bank'], drug_name=row['drug_name'], indication=row['Indication'], state=row['state'], iupac_name_seq=row['IUPAC_name'])
        g, created = Geneagmp.objects.get_or_create(gene_name=row['gene_name'], gene_id=row['curated_gene_symbol'], chromosome=row['chromosome'], uniprot_ac=row['uniprot'], function=row['function'])
        v = Variantagmp(studyagmp=s, drugagmp=d, phenotypeagmp=p, geneagmp=g, variant_type=row['variant_type'], source_db=row['source'], id_in_source_db=row['id_in_source'], rs_id=row['id'])
        v.save()

        normalized_01_p_value = normalize_01_p_value(row['p-value'])

        vs = VariantStudyagmp(studyagmp=s, variantagmp=v,
                              latitude_01=row['latitude_01'], longitude_01=row['longitude_01'],
                              latitude_02=row['latitude_02'], longitude_02=row['longitude_02'],
                              latitude_03=row['latitude_03'], longitude_03=row['longitude_03'],
                            #   p_value=row['p-value'],
                              p_value=normalized_01_p_value,
                              ethnicity=row['Ethnicity'],
                              mixed_population=row['mixed_population'],
                              geographical_regions=row['geographical_region'],
                              country_participant=row['origin_of_participants'],
                              )
        vs.save()

    no_of_genes = Geneagmp.objects.all().count()
    no_of_drugs = Drugagmp.objects.all().count()
    no_of_variants = Variantagmp.objects.all().count()
    no_of_studies = Studyagmp.objects.all().count()
    no_of_phenotypes = Phenotypeagmp.objects.all().count()
    no_of_variant_studies = VariantStudyagmp.objects.all().count()

    print("\n")
    print(f"{no_of_phenotypes}: PHENOTYPES IMPORTED")
    print(f"{no_of_studies}: Studies IMPORTED")
    print(f"{no_of_genes}: Genes IMPORTED") 
    print(f"{no_of_drugs}: DRUGS IMPORTED") 
    print(f"{no_of_variant_studies}: VARIANT STUDIES IMPORTED") 
    print(f"{no_of_variants}: VARIANTS IMPORTED \n")
    print("\n")
    print("############ First JOB ENDED ################")

    # Import data from the second Excel file
    df_excel = pd.read_excel('import_csv/second_import_job_run_sept_2024.xlsx')

    # replaces NS and nan with NR
    def normalize_p_value(value):
        if pd.isna(value) or value in ['NS', 'nan']:
            return 'NR'
        return value

    # removed the drug_bank_id=row['ID Drug bank'], in drug second import job run
    for index, row in df_excel.iterrows():
        print(row)
        p01, created = Phenotypeagmp.objects.get_or_create(name=row['phenotype'])
        s01, created = Studyagmp.objects.get_or_create(data_ac=row['data_ac'], publication_id=row['PUBMEDID'], publication_year=row['publication_year'], study_type=row['study_type'], title=row['title'])
        g01, created = Geneagmp.objects.get_or_create(gene_name=row['gene_name'], gene_id=row['curated_gene_symbol'], chromosome=row['chromosome'], uniprot_ac=row['uniprot'], function=row['function'])
        v01 = Variantagmp(studyagmp=s01, phenotypeagmp=p01, geneagmp=g01, variant_type=row['variant_type'], source_db=row['source'], id_in_source_db=row['id_in_source'], rs_id=row['id'])
        v01.save()
        
        normalized_p_value = normalize_p_value(row['p-value'])

        vs01 = VariantStudyagmp(studyagmp=s01, variantagmp=v01,
                                latitude_01=row['latitude_01'], longitude_01=row['longitude_01'],
                                latitude_02=row['latitude_02'], longitude_02=row['longitude_02'],
                                latitude_03=row['latitude_03'], longitude_03=row['longitude_03'],
                                latitude_04=row['latitude_04'], longitude_04=row['longitude_04'],
                                latitude_05=row['latitude_05'], longitude_05=row['longitude_05'],
                                latitude_06=row['latitude_06'], longitude_06=row['longitude_06'],
                                latitude_07=row['latitude_07'], longitude_07=row['longitude_07'],
                                latitude_08=row['latitude_08'], longitude_08=row['longitude_08'],
                                latitude_09=row['latitude_09'], longitude_09=row['longitude_09'],
                                latitude_10=row['latitude_10'], longitude_10=row['longitude_10'],
                                latitude_11=row['latitude_11'], longitude_11=row['longitude_11'],
                                # p_value=row['p-value'],
                                p_value=normalized_p_value,
                                ethnicity=row['Ethnicity'],
                                mixed_population=row['mixed_population'],
                                geographical_regions=row['geographical_region'],
                                country_participant=row['origin_of_participants'],
                                )
        vs01.save()

    new_no_of_genes = Geneagmp.objects.all().count()
    # new_no_of_drugs = Drugagmp.objects.all().count()
    new_no_of_variants = Variantagmp.objects.all().count()
    new_no_of_studies = Studyagmp.objects.all().count()
    new_no_of_phenotypes = Phenotypeagmp.objects.all().count()
    new_no_of_variant_studies = VariantStudyagmp.objects.all().count()

    print("\n")
    print(f"{new_no_of_phenotypes}: TOTAL PHENOTYPES IMPORTED")
    print(f"{new_no_of_studies}: TOTAL Studies IMPORTED")
    print(f"{new_no_of_genes}: TOTAL Genes IMPORTED") 
    # print(f"{new_no_of_drugs}: TOTAL DRUGS IMPORTED") 
    print(f"{new_no_of_variant_studies}: TOTAL VARIANT STUDIES IMPORTED") 
    print(f"{new_no_of_variants}: TOTAL VARIANTS IMPORTED \n")
    print("############ SECOND JOB ENDED & GWAS Catalogue IMPORT COMPLETE ################")







