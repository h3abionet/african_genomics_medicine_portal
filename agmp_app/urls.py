from django.urls import path, re_path, include
# from django.conf.urls import url

from . import views
from .views import (DrugagmpDetailView, PhamacogeneDrugAssoc, VariantStudyagmpListView,VarDrugAssocDetailView,VvarDrugAssocDetailView,DiseaseVariantDetailView,VarDisAssocDetailView, PharmacoDrugDetailView,VariantDiseaseAssocDetailView,VariantDrugAssociationDetailView,search_view)

urlpatterns = [
    path('', search_view, name='search_view'),
    path('about', views.about, name='about'),
#  old url for search   path('search_v', views.search_all, name='search_v'),  
    path('home', views.home, name='home'),
    #new views
    path('drug-detail/<int:pk>/', DrugagmpDetailView.as_view(), name='drug-detail'),
    path('variant-drug-list/<int:pk>/',VariantStudyagmpListView.as_view(), name='variant-drug-list'),
     ##### New URLS for data tables ######
    path('PhamacogeneDrugAssoc/<str:gene_id>/',
         PhamacogeneDrugAssoc.as_view(),
         name='PhamacogeneDrugAssoc'),

    path('VarDrugAssoc/<str:rs_id>/',
         VarDrugAssocDetailView.as_view(),
         name='Var_Drug_Assoc'),

    
    path('VariantDiseaseAssoc/<str:rs_id>/',
         VariantDiseaseAssocDetailView.as_view(),
         name='Variant_Disease_Assoc'),


    path('VvarDrugAssoc/<str:rs_id>/',
         VvarDrugAssocDetailView.as_view(),
         name='Vvar_Drug_Assoc'),

    path('VarDisAssoc/<str:rs_id>/',
         VarDisAssocDetailView.as_view(),
         name='Var_Dis_Assoc'),

    path('PharmacoDrug/<str:gene_id>/',
         PharmacoDrugDetailView.as_view(),
         name='Pharmaco_Drug_Detail'),

    path('VariantDrugAssociation/<str:drug_id>/',
         VariantDrugAssociationDetailView.as_view(),
         name='VariantDrugAssociation'),

     
    path('DiseaseVariant/<str:phenotypeagmp__name>/',
         DiseaseVariantDetailView.as_view(),
         name='DiseaseVariant'),

     ##### New URLS for data tables ######

    # call search query with optional parameters 
    path('summary/', views.summary, name='summary'),
    path('resources/', views.resources, name='resources'),
    path('outreach/', views.outreach, name='outreach'),
    path('contact/', views.contact, name='contact'),
    path('databases/', views.databases, name='databases'),
    path('tools_pipelines/', views.tools_pipelines, name='tools_pipelines'),
    path('online_courses/', views.online_courses, name='online_courses'),
    path('disclaimer', views.disclaimer, name='disclaimer'),
    path('faqs', views.faqs, name='faqs'),
    path('tutorial/', views.tutorial, name='tutorial'),
    path('help', views.help, name='help'),
    path('agnocomplete/', include('agnocomplete.urls')),
]
