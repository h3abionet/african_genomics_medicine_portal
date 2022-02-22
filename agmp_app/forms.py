from django import forms
from .models import pharmacogenes, CountryData

class PostForm(forms.ModelForm):
    class Meta:
        model = pharmacogenes
        # list fields
        fields = ('gene_name', 'function')
        error_css_class = 'error'
        required_css_class = 'bold'
        # https://www.webforefront.com/django/formtemplatelayout.html
        # TODO: allow empty fields

class CountryDataFrom(forms.ModelForm):
    class Meta:
        model = CountryData
        fields = '__all__'
