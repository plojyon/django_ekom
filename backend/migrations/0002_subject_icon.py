# Generated by Django 3.2.5 on 2021-07-22 13:09

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='subject',
            name='icon',
            field=models.CharField(default='fa fa-language', max_length=20),
        ),
    ]
