from agnocomplete.register import register
from agnocomplete.core import AgnocompleteChoices, AgnocompleteModel
#from .models import Index
from django.utils.functional import cached_property
from copy import copy
import logging

logger = logging.getLogger(__name__)
_omni = []

# class Search(AgnocompleteModel):
#     model = Index
#     fields = ['recname', 'keywords']
#     value_key = 'recname'
#     label_key = 'recname'

#     def item(self, current_item):
#         return dict(
#             value=current_item.recname,
#             label=current_item.recname,
#         )       

# # Register models
# register(Search)