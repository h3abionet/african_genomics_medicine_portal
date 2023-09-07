import csv
import numpy as np
from agmp_app.models import Variantagmp, Drugagmp, Geneagmp, Studyagmp, Phenotypeagmp, VariantStudyagmp
# python3 manage.py runscript load_data
# g is for Gene
# d is for Drug
# v is for Variant
# s is for Study
# p is for Phenotype


def run():

    fhand = open('csv/final_agmp_import_05_sept_23.csv',encoding='latin-1')
    # fhand = open('csv/data_AGMP_NotesRemoved.csv',encoding='latin-1')
    reader = csv.reader(fhand)
    next(reader)  # Advance past the header

    Variantagmp.objects.all().delete()
    Drugagmp.objects.all().delete()
    Geneagmp.objects.all().delete()
    Studyagmp.objects.all().delete()
    Phenotypeagmp.objects.all().delete()
    VariantStudyagmp.objects.all().delete()
    
    # print("Import running ....")
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
    print(" ############ JOB ENDED ################ ")








