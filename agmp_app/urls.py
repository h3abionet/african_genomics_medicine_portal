from django.urls import path, re_path
# from django.conf.urls import url

from . import views

urlpatterns = [
    path('', views.index, name='index'),
    path('about/', views.about, name='about'),
    path('search/', views.search, name='search'),
    path('search_details/<str:db_name>/<int:query_id>', views.search_details, name='search_details'),
    path('resources/', views.resources, name='resources'),
    path('contact/', views.contact, name='contact'),
]