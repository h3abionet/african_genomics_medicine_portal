from rest_framework import serializers
from .models import Variantagmp, Geneagmp, Drugagmp, Studyagmp, Phenotypeagmp


class VariantagmpSerializer(serializers.ModelSerializer):
    # Optional: include related object details instead of just IDs
    gene_name = serializers.CharField(source='geneagmp.gene_name', read_only=True)
    drug_name = serializers.CharField(source='drugagmp.drug_name', read_only=True)
    
    class Meta:
        model = Variantagmp
        fields = '__all__'