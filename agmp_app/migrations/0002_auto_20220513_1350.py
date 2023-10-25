# Generated by Django 2.2.24 on 2022-05-13 13:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agmp_app', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CountryData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country', models.CharField(max_length=100)),
                ('population', models.IntegerField()),
            ],
            options={
                'verbose_name_plural': 'Country Population Data',
            },
        ),
    ]