# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-26 07:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('rbac', '0007_auto_20200126_1555'),
    ]

    operations = [
        migrations.AlterField(
            model_name='menu',
            name='icon',
            field=models.CharField(blank=True, max_length=64, null=True, verbose_name='图标'),
        ),
    ]
