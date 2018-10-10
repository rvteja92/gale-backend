# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-08 18:13
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crawler', '0003_auto_20181007_1449'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='entry',
            name='images',
        ),
        migrations.AddField(
            model_name='entry',
            name='images_array',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(validators=[django.core.validators.URLValidator]), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='entry',
            name='links',
            field=django.contrib.postgres.fields.ArrayField(base_field=models.TextField(validators=[django.core.validators.URLValidator]), blank=True, null=True, size=None),
        ),
        migrations.AlterField(
            model_name='entry',
            name='url',
            field=models.TextField(unique=True, validators=[django.core.validators.URLValidator]),
        ),
    ]
