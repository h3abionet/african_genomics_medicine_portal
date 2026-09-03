from django.urls import path, re_path, include
from rest_framework.routers import DefaultRouter
from .api_views import VariantagmpViewSet
from . import views
from .views import (
    DrugagmpDetailView,
    PhamacogeneDrugAssoc,
    VariantStudyagmpListView,
    VarDrugAssocDetailView,
    VvarDrugAssocDetailView,
    DiseaseVariantDetailView,
    VarDisAssocDetailView,
    PharmacoDrugDetailView,
    VariantDiseaseAssocDetailView,
    VariantDrugAssociationDetailView,
    search_view,
    test_data_table,
    # Batch Query Views
    batch_query_view,
    batch_query_execute,
    batch_query_export,
    batch_query_export_xlsx,
)

router = DefaultRouter()
router.register(r'variants', VariantagmpViewSet, basename='variant')

urlpatterns = [
    path('test', test_data_table, name='test_data_table'),
    path('', search_view, name='search_view'),
    path('about', views.about, name='about'),
    path('get-map-data/<str:map_type>/', views.get_map_data, name='get_map_data'),
    path('home', views.home, name='home'),

    # Detail views
    path('drug-detail/<int:pk>/', DrugagmpDetailView.as_view(), name='drug-detail'),
    path('variant-drug-list/<int:pk>/', VariantStudyagmpListView.as_view(), name='variant-drug-list'),

    # Data tables
    path('drug-phenotype-associations/<str:gene_id>/',
         PhamacogeneDrugAssoc.as_view(),
         name='drug_phenotype_associations'),
    path('variant-drug/<str:rs_id>/',
         VariantDrugAssociationDetailView.as_view(),
         name='variant_drug'),
    path('variant-phenotype/<str:rs_id>/',
         VariantDiseaseAssocDetailView.as_view(),
         name='variant_phenotype'),
    path('VvarDrugAssoc/<str:rs_id>/',
         VvarDrugAssocDetailView.as_view(),
         name='Vvar_Drug_Assoc'),
    path('VarDisAssoc/<str:rs_id>/',
         VarDisAssocDetailView.as_view(),
         name='Var_Dis_Assoc'),
    path('PharmacoDrug/<str:gene_id>/',
         PharmacoDrugDetailView.as_view(),
         name='Pharmaco_Drug_Detail'),

    # CHANGED: <str:> to <path:> so phenotype names with / ( ) work
    path('DiseaseVariant/<path:phenotypeagmp__name>/',
         DiseaseVariantDetailView.as_view(),
         name='DiseaseVariant'),

    # Static pages
    path('summary/', views.summary, name='summary'),
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

    # =========================================
    # BATCH QUERY URLs
    # =========================================
    path('batch-query/', batch_query_view, name='batch_query'),
    path('batch-query/execute/', batch_query_execute, name='batch_query_execute'),
    path('batch-query/export/', batch_query_export, name='batch_query_export'),
    path('batch-query/export-xlsx/', batch_query_export_xlsx, name='batch_query_export_xlsx'),

    # API urls
    path('api/', include(router.urls)),
]