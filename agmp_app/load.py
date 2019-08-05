import pandas as pd
from .models import drug, pharmacogenes				

#populate the drug table
def populate_drug():
    df = pd.read_csv("/Users/macbook/Desktop/dummy_data/drug.csv")
    #print(df)
    for index, row in df.iterrows():
        drug.objects.update_or_create(
            drug_id=row['drug_id'],
            drug_name=row['drug_name'],
            posology=row['posolgy'],
            chemical_structure=row['chemical_structure'],
            drug_bank_id=row['drug_bank_id'],
            state_id=row['state']
            )

def populate_genes():
    df = pd.read_csv("/Users/macbook/Desktop/dummy_data/pharmacogenes.csv")
    #print(df)
    for index, row in df.iterrows():
        pharmacogenes.objects.update_or_create(
            id=row['id'],
            gene_name=row['gene_name'],
            protein=row['protein'],
            function=row['function']
            )