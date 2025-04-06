from django import forms
from .models import PhenotypeSubmissionagmp
from django.core.validators import RegexValidator
import re
from django_recaptcha.fields import ReCaptchaField
from django_countries.fields import CountryField 
from django_countries.widgets import CountrySelectWidget




class ModelSelectForm(forms.Form):
    MODELS = [
        ('product', 'Product'),
        # Add more models as needed
    ]

    model_choice = forms.ChoiceField(choices=MODELS, widget=forms.RadioSelect)
    search_query = forms.CharField(max_length=100, required=False, widget=forms.TextInput(attrs={'id': 'autocomplete'}))





class SearchForm(forms.Form):
    SEARCH_CHOICES = (
        ('Variantagmp', 'Variant'),
        ('Geneagmp', 'Gene'),
        ('Drugagmp', 'Drug'),
        ('Disease', 'Disease'),
    )
    search_option = forms.ChoiceField(choices=SEARCH_CHOICES, widget=forms.RadioSelect,label="Choose a category to search by")
    search_query = forms.CharField(max_length=100)


class ModelSearchForm(forms.Form):


    MODELS_CHOICES = [
        ('variantagmp', 'Variant'),
        ('geneagmp', 'Gene'),
        ('drugagmp', 'Drug'),
        ('disease', 'Disease'),
    ]

    model_selection = forms.ChoiceField(choices=MODELS_CHOICES, widget=forms.RadioSelect,label="Choose a category to search by")
    search_query = forms.CharField(max_length=100, required=False, label="Search")




class PhenotypeSubmissionForm(forms.ModelForm):
    country = CountryField().formfield(widget=CountrySelectWidget())
    captcha = ReCaptchaField()
    orcid_id = forms.CharField(
        max_length=500,
        required=True,
        validators=[RegexValidator(
            regex=r'^\d{4}-\d{4}-\d{4}-\d{3}[\dX]$',
            message='Invalid ORCID ID format. Expected format: XXXX-XXXX-XXXX-XXXX.',
            flags=re.IGNORECASE,
        )],
        widget=forms.TextInput(attrs={'placeholder': 'XXXX-XXXX-XXXX-XXXX'}),
    )
    
    pmid_id = forms.CharField(
        max_length=8,
        required=True,
        validators=[RegexValidator(
            regex=r'^\d{8}$',
            message='Invalid PMID ID format. Expected format: 8 digits.',
        )],
        widget=forms.TextInput(attrs={'placeholder': 'Enter PMID ID'}),
    )
    
    doi = forms.CharField(
        max_length=100,
        required=True,
        validators=[RegexValidator(
            regex=r'^10\.\d{4,9}/[-._;()/:A-Z0-9]+$',
            message='Invalid DOI format. Expected format: 10.xxxxx/yyyyy.',
        )],
        widget=forms.TextInput(attrs={'placeholder': 'Enter DOI'}),
    )

    ethnicity = forms.ChoiceField(
        choices=[
            ('', 'Select Ethnicity'),
            ('Caucasian', 'Caucasian'),
            ('African American', 'African American'),
            ('Hispanic', 'Hispanic'),
            ('Asian', 'Asian'),
            ('Other', 'Other'),
        ],
        required=True
    )
    
    AA_PARTICIPANTS_CHOICES = [
        ('', 'Select Option'),
        ('Yes', 'Yes'),
        ('No', 'No'),
        ('Not sure', 'Not sure'),
    ]
    aa_participants = forms.ChoiceField(choices=AA_PARTICIPANTS_CHOICES, required=True)

    class Meta:
        model = PhenotypeSubmissionagmp
        fields = ['orcid_id', 'pmid_id', 'doi', 'phenotype_of_interest', 'upload_file', 'country', 'ethnicity', 'aa_participants', 'captcha']