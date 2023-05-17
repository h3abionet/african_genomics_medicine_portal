from django.urls import path, re_path, include
# from django.conf.urls import url
# from core.views import BootstrapFilterView
from . import views
from .views import DrugDetailView, GeneDetailView, DrugagmpDetailView, VariantStudyagmpListView, Drug2DetailView



urlpatterns = [
    # path('', views.home, name='index'),
    path('about', views.about, name='about'),
    path('', views.search, name='search'),
    path('home', views.home, name='home'),

    # call search query with optional parameters 
    path('search/<str:query_string>', views.query, kwargs={'disease': 0, 'drug': 0, 'variant': 0, 'gene': 0}, name='query'),
    path('search_details/<str:search_type>/<str:query_id>', views.search_details, name='search_details'),
    path('summary/', views.summary, name='summary'),
    path('summary/countries', views.country_summary, name='country_summary'),
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
    path('search-variant/',views.FilterView, name='search-variant'),
    path('search-drug/',views.FilterViewDrug, name='search-drug'),
    path('search-gene/',views.FilterViewGene, name='search-gene'),
    path('search-disease/',views.FilterViewDisease, name='search-disease'),
    path('agnocomplete/', include('agnocomplete.urls')),
    path('search-all/', views.search_all, name='search_v'),
    path('drug-list/', views.drug_list_view, name='drug_list'),
    path('drug/<str:drug_id>/',
         DrugDetailView.as_view(),
         name='drug_detail'),
    path('gene/<str:gene_id>/',
         GeneDetailView.as_view(),
         name='gene_detail'),
     path('drug-detail/<int:pk>/', DrugagmpDetailView.as_view(), name='drug-detail'),
     path('variant-drug-list/<int:pk>/',VariantStudyagmpListView.as_view(), name='variant-drug-list'),
     path('variant-drug2/<str:drug_id>/',
         Drug2DetailView.as_view(),
         name='variant_detail'),
]

  


