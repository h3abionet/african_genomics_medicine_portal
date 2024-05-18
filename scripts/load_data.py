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


def run():

    fhand = open('csv/first_import_job_run.csv',encoding='latin-1')
    reader = csv.reader(fhand)
    next(reader)  # Advance past the header

    Variantagmp.objects.all().delete()
    Drugagmp.objects.all().delete()
    Geneagmp.objects.all().delete()
    Studyagmp.objects.all().delete()
    Phenotypeagmp.objects.all().delete()
    VariantStudyagmp.objects.all().delete()
    
    
    for row in reader:
      
        print(row)
        p, created = Phenotypeagmp.objects.get_or_create(name=row[2])
        s, created = Studyagmp.objects.get_or_create(data_ac=row[15], publication_id=row[1], publication_year=row[19], study_type=row[9], title=row[17], publication_type=row[16])
        d, created = Drugagmp.objects.get_or_create(drug_name=row[23], indication=row[26], drug_bank_id=row[24], iupac_name_seq=row[27],state=row[25])
        g, created = Geneagmp.objects.get_or_create(gene_name=row[11],gene_id=row[10],chromosome=row[12],function=row[14],uniprot_ac=row[13])
        v = Variantagmp(studyagmp=s,drugagmp=d,phenotypeagmp=p, geneagmp=g, source_db=row[20], id_in_source_db=row[2], variant_type=row[21], rs_id=row[0],)
        v.save()
        vs = VariantStudyagmp(studyagmp=s,variantagmp=v,country_participant=row[3], country_participant_01=row[29],country_participant_02=row[30],country_participant_03=row[31],country_participant_04=row[32],country_participant_05=row[33],country_participant_06=row[34],country_participant_07=row[35], geographical_regions=row[4], p_value=row[7], ethnicity=row[5], notes=row[28],
                               latitude_01=row[36],longitude_01=row[37],
                               latitude_02=row[38],longitude_02=row[39],
                               latitude_03=row[40],longitude_03=row[41],
                               latitude_04=row[42],longitude_04=row[43],
                               latitude_05=row[44],longitude_05=row[45],
                               latitude_06=row[46],longitude_06=row[47],
                               latitude_07=row[48],longitude_07=row[49],
                               
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
    print(f"{no_of_variant_studies}: VARIENT STUDIES-IMPORTED") 
    print(f"{no_of_variants}: VARIANTS IMPORTED \n")

    print(f" \n")
    print(f" \n")
    print(" ############ First JOB ENDED ################ ")




    ################### April May 2024 ####################################
    df = pd.read_csv('csv/second_import_job_run.csv',encoding='latin-1')


    for index, row in df.iterrows():
      
        print(row)
        p01, created = Phenotypeagmp.objects.get_or_create(name=row['phenotype'])
        s01, created = Studyagmp.objects.get_or_create(data_ac=row['data_ac'],publication_id=row['publication'], publication_year=row['publication_year'], study_type=row['study_type'], title=row['title'])
        d01, created = Drugagmp.objects.get_or_create(drug_id=row['ID Drug bank'],drug_name=row['drug_name'],indication=row['Indication'],state=row['state'],iupac_name_seq=row['IUPAC_name'])
        g01, created = Geneagmp.objects.get_or_create(gene_name=row['gene_name'],gene_id=row['curated_gene_symbol'],chromosome=row['chromosome'],uniprot_ac=row['uniprot'],function=row['function'])
        v01 = Variantagmp(studyagmp=s01,drugagmp=d01,phenotypeagmp=p01, geneagmp=g01, variant_type=row['variant_type'], source_db=row['source'], id_in_source_db=row['id_in_source'], rs_id=row['id'])
        v01.save()
        vs01 = VariantStudyagmp(studyagmp=s01,variantagmp=v01,
                               latitude_01=row['latitude_01'],longitude_01=row['longitude_01'],
                               latitude_02=row['latitude_02'],longitude_02=row['longitude_02'],
                               latitude_03=row['latitude_03'],longitude_03=row['longitude_03'],
                               latitude_04=row['latitude_04'],longitude_04=row['longitude_04'],
                               latitude_05=row['latitude_05'],longitude_05=row['longitude_05'],
                               latitude_06=row['latitude_06'],longitude_06=row['longitude_06'],
                               latitude_07=row['latitude_07'],longitude_07=row['longitude_07'],
                               p_value=row['p-value'],
                               ethnicity=row['Ethnicity'],
                               geographical_regions=row['geographical_region'],


                               
                               )
        vs01.save()


        new_no_of_genes = Geneagmp.objects.all().count()
        new_no_of_drugs = Drugagmp.objects.all().count()
        new_no_of_variants = Variantagmp.objects.all().count()
        new_no_of_studies = Studyagmp.objects.all().count()
        new_no_of_phenotypes = Phenotypeagmp.objects.all().count()
        new_no_of_variant_studies = VariantStudyagmp.objects.all().count()

    print("\n")
    print(f"{new_no_of_phenotypes}: TOTAL PHENOTYPES IMPORTED")
    print(f"{new_no_of_studies}: TOTAL Studies IMPORTED")
    print(f"{new_no_of_genes}: TOTAL Genes IMPORTED") 
    print(f"{new_no_of_drugs}: TOTAL DRUGS IMPORTED") 
    print(f"{new_no_of_variant_studies}: TOTAL VARIENT STUDIES-IMPORTED") 
    print(f"{new_no_of_variants}: TOTAL VARIANTS IMPORTED \n")
    print(" ############ SECOND JOB ENDED& GWAS Catalogue IMPORT COMPLETE ################ ")









