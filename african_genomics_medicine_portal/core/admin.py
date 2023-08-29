from django.contrib import admin

# Register your models here.
from .models import Author, Category, Journal

admin.site.register(Author)
admin.site.register(Category)
admin.site.register(Journal)