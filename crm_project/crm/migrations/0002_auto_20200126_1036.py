# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-01-26 02:36
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('crm', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='enrollment',
            name='contract_agreed',
            field=models.BooleanField(default=False, verbose_name='已认真阅读完培训协议并同意全部协议内容'),
        ),
    ]
