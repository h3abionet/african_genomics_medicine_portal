# Generated by Django 2.2.24 on 2023-01-15 23:09

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('agmp_app', '0002_auto_20221025_1502'),
    ]

    operations = [
        migrations.AddField(
            model_name='variantstudyagmp',
            name='studyagmp',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='agmp_app.Studyagmp'),
        ),
    ]
