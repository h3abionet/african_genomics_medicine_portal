# Generated by Django 3.2.18 on 2023-10-24 23:35

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('agmp_app', '0002_auto_20230815_1153'),
    ]

    operations = [
        migrations.CreateModel(
            name='Aaaa',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Bbbb',
            fields=[
                ('id', models.BigAutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(blank=True, max_length=500, null=True)),
            ],
        ),
    ]