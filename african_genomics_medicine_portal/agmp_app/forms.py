from django import forms

# Define the models to be searched
from .models import Variantagmp, Drugagmp, Geneagmp


class SearchForm(forms.Form):
    SEARCH_CHOICES = (
        ('Variantagmp', 'Variant'),
        ('Geneagmp', 'Gene'),
        ('Drugagmp', 'Drug'),
        ('Disease', 'Disease'),
    )
    search_option = forms.ChoiceField(choices=SEARCH_CHOICES, widget=forms.RadioSelect,label="Choose a category to search by")
    search_query = forms.CharField(max_length=100)