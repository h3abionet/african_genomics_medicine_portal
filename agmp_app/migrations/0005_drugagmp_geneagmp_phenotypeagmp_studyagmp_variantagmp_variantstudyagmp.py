# Generated by Django 3.2.18 on 2023-09-25 21:18

import agmp_app.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agmp_app', '0004_auto_20220808_1933'),
    ]

    operations = [
        migrations.CreateModel(
            name='Drugagmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('drug_bank_id', models.CharField(blank=True, max_length=500, null=True)),
                ('drug_name', models.CharField(blank=True, max_length=500, null=True)),
                ('indication', models.TextField(blank=True, max_length=500, null=True)),
                ('iupac_name_seq', models.CharField(blank=True, max_length=500, null=True)),
                ('state', models.CharField(blank=True, max_length=500, null=True)),
                ('drug_id', models.CharField(blank=True, default=agmp_app.models.increment_drug_id, max_length=255, null=True)),
            ],
            options={
                'verbose_name_plural': '* Drugs',
            },
        ),
        migrations.CreateModel(
            name='Geneagmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('gene_id', models.CharField(blank=True, max_length=500, null=True)),
                ('chromosome', models.CharField(blank=True, max_length=500, null=True)),
                ('function', models.TextField(blank=True, max_length=500, null=True)),
                ('gene_name', models.CharField(blank=True, max_length=500, null=True)),
                ('uniprot_ac', models.CharField(blank=True, max_length=500, null=True)),
            ],
            options={
                'verbose_name_plural': '* Gene',
            },
        ),
        migrations.CreateModel(
            name='Phenotypeagmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.TextField(blank=True, max_length=500, null=True)),
            ],
            options={
                'verbose_name_plural': '* Phenotype',
            },
        ),
        migrations.CreateModel(
            name='Studyagmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data_ac', models.CharField(blank=True, max_length=500, null=True)),
                ('publication_id', models.CharField(blank=True, max_length=500, null=True)),
                ('publication_type', models.CharField(blank=True, max_length=500, null=True)),
                ('publication_year', models.CharField(blank=True, max_length=50, null=True)),
                ('study_type', models.CharField(blank=True, max_length=500, null=True)),
                ('title', models.TextField(blank=True, max_length=500, null=True)),
            ],
            options={
                'verbose_name_plural': '* Studies',
            },
        ),
        migrations.CreateModel(
            name='Variantagmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('allele', models.CharField(blank=True, max_length=500, null=True)),
                ('source_db', models.CharField(blank=True, max_length=500, null=True)),
                ('id_in_source_db', models.CharField(blank=True, max_length=500, null=True)),
                ('rs_id_star_annotation', models.CharField(blank=True, max_length=500, null=True)),
                ('variant_type', models.CharField(blank=True, max_length=500, null=True)),
                ('rs_id', models.CharField(blank=True, max_length=500, null=True)),
                ('drugagmp', models.ForeignKey(blank=True, default='DRUG', null=True, on_delete=django.db.models.deletion.CASCADE, related_name='drugs', to='agmp_app.drugagmp')),
                ('geneagmp', models.ForeignKey(blank=True, default='GENE', null=True, on_delete=django.db.models.deletion.CASCADE, to='agmp_app.geneagmp')),
                ('phenotypeagmp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='agmp_app.phenotypeagmp')),
                ('studyagmp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, related_name='studys', to='agmp_app.studyagmp')),
            ],
            options={
                'verbose_name_plural': '* Variant',
            },
        ),
        migrations.CreateModel(
            name='VariantStudyagmp',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('country_participant', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude', models.CharField(blank=True, max_length=500, null=True)),
                ('longitude', models.CharField(blank=True, max_length=500, null=True)),
                ('country_participant_01', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude_01', models.CharField(blank=True, max_length=500, null=True)),
                ('longitude_01', models.CharField(blank=True, max_length=500, null=True)),
                ('country_participant_02', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude_02', models.CharField(blank=True, max_length=500, null=True)),
                ('longitude_02', models.CharField(blank=True, max_length=500, null=True)),
                ('country_participant_03', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude_03', models.CharField(blank=True, max_length=500, null=True)),
                ('longitude_03', models.CharField(blank=True, max_length=500, null=True)),
                ('country_participant_04', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude_04', models.CharField(blank=True, max_length=500, null=True)),
                ('longitude_04', models.CharField(blank=True, max_length=500, null=True)),
                ('country_participant_05', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude_05', models.CharField(blank=True, max_length=500, null=True)),
                ('longitude_05', models.CharField(blank=True, max_length=500, null=True)),
                ('country_participant_06', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude_06', models.CharField(blank=True, max_length=500, null=True)),
                ('longitude_06', models.CharField(blank=True, max_length=500, null=True)),
                ('country_participant_07', models.CharField(blank=True, max_length=500, null=True)),
                ('latitude_07', models.CharField(blank=True, max_length=500, null=True)),
                ('longitude_07', models.CharField(blank=True, max_length=500, null=True)),
                ('ethnicity', models.CharField(blank=True, max_length=500, null=True)),
                ('geographical_regions', models.CharField(blank=True, max_length=500, null=True)),
                ('notes', models.TextField(blank=True, max_length=500, null=True)),
                ('p_value', models.CharField(blank=True, max_length=500, null=True)),
                ('studyagmp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='agmp_app.studyagmp')),
                ('variantagmp', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='agmp_app.variantagmp')),
            ],
            options={
                'verbose_name_plural': '* Variant Studies',
            },
        ),
    ]
