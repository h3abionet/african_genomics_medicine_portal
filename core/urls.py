from django.urls import path, re_path, include
# from django.conf.urls import url
# from core.views import BootstrapFilterView
from core.views import BootstrapFilterView

from . import views

urlpatterns = [
     path('test/',views.BootstrapFilterView, name='bootstrap'),

]