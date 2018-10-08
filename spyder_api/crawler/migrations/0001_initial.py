# -*- coding: utf-8 -*-
# Generated by Django 1.11 on 2018-10-07 12:54
from __future__ import unicode_literals

import django.contrib.postgres.fields
import django.contrib.postgres.fields.jsonb
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Entry',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('url', models.URLField(unique=True)),
                ('links', django.contrib.postgres.fields.ArrayField(base_field=models.URLField(), blank=True, null=True, size=None)),
                ('images', django.contrib.postgres.fields.jsonb.JSONField(blank=True, null=True)),
                ('complete', models.BooleanField(default=False)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('modified_at', models.DateTimeField(auto_now=True)),
                ('parent', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='child_links', to='crawler.Entry')),
            ],
        ),
    ]
