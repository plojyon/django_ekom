# Generated by Django 3.2.5 on 2021-07-26 07:16

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('backend', '0003_alter_submission_year'),
    ]

    operations = [
        migrations.AlterField(
            model_name='submission',
            name='professor',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.PROTECT, to='backend.professor'),
        ),
    ]