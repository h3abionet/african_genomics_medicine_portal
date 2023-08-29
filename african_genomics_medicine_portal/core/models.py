from django.db import models

# Create your models here.
import secrets
from core.utils import custom_id

class Author(models.Model):
    name= models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name

class Category(models.Model):
    name =  models.CharField(max_length=250, null=True, blank=True)

    def __str__(self):
        return self.name


class Journal(models.Model):
    title = models.CharField(max_length=250, null=True, blank=True)
    author = models.ForeignKey(Author, on_delete=models.CASCADE)
    categories = models.ManyToManyField(Category)
    publish_date = models.DateField(auto_now_add=True)
    views = models.IntegerField(default=0)
    reviewed = models.BooleanField(default=False)
    custom_id = models.CharField(primary_key=True, max_length=11, unique=True, default=custom_id)



    def __str__(self):
        return self.title