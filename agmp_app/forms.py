from django import forms
from django import forms
from django.utils.translation import ugettext_lazy as _
from .models import drug

from .models import pharmacogenes

class PostForm(forms.ModelForm):
    class Meta:
        model = pharmacogenes
        # list fields
        fields = ('gene_name', 'function')
        error_css_class = 'error'
        required_css_class = 'bold'
        # https://www.webforefront.com/django/formtemplatelayout.html
        # TODO: allow empty fields



# myproject/apps/music/forms.py


class drugForm(forms.ModelForm):
    class Meta:
        model = drug
        fields = "__all__" 