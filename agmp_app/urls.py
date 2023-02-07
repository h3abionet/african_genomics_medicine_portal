from django.urls import path, re_path, include
# from django.conf.urls import url
# from core.views import BootstrapFilterView

from . import views

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
    path('search-new/',views.FilterView, name='bootstrap'),
    path('agnocomplete/', include('agnocomplete.urls')),
]
