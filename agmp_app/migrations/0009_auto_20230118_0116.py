# Generated by Django 2.2.24 on 2023-01-18 01:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agmp_app', '0008_auto_20230118_0111'),
    ]

    operations = [
        migrations.AlterField(
            model_name='geneagmp',
            name='function',
            field=models.TextField(blank=True, max_length=50, null=True),
        ),
    ]
