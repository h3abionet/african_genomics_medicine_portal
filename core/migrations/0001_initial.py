# Generated by Django 2.2.24 on 2023-02-09 11:01

import core.utils
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Author',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=250, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Journal',
            fields=[
                ('title', models.CharField(blank=True, max_length=250, null=True)),
                ('publish_date', models.DateField(auto_now_add=True)),
                ('views', models.IntegerField(default=0)),
                ('reviewed', models.BooleanField(default=False)),
                ('custom_id', models.CharField(default=core.utils.custom_id, max_length=11, primary_key=True, serialize=False, unique=True)),
                ('author', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to='core.Author')),
                ('categories', models.ManyToManyField(to='core.Category')),
            ],
        ),
    ]