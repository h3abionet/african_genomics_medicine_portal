# Generated by Django 3.2.22 on 2023-11-13 23:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agmp_app', '0006_delete_countrydata'),
    ]

    operations = [
        migrations.CreateModel(
            name='Product',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
                ('description', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
    ]
