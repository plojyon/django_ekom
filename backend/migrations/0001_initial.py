# Generated by Django 3.2.5 on 2021-07-22 09:49

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Professor',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('first_name', models.CharField(max_length=50)),
                ('last_name', models.CharField(max_length=50)),
                ('username', models.CharField(max_length=50)),
                ('password', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Subject',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
                ('slug', models.CharField(max_length=10, unique=True)),
            ],
        ),
        migrations.CreateModel(
            name='Tag',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=50)),
            ],
        ),
        migrations.CreateModel(
            name='Submission',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('title', models.CharField(max_length=150)),
                ('author', models.CharField(max_length=50)),
                ('year', models.IntegerField(choices=[(0, 'Neznan'), (1, 'Prvi'), (2, 'Drugi'), (3, 'Tretji'), (4, 'Četrti')], default=0)),
                ('type', models.IntegerField(choices=[(0, 'Drugo'), (1, 'Zapiski'), (2, 'Test'), (3, 'Naloge'), (4, 'Laboratorijske vaje')], default=0)),
                ('uploaded', models.DateTimeField(auto_now_add=True, null=True)),
                ('file', models.FileField(blank=True, null=True, upload_to='')),
                ('professor', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='backend.professor')),
                ('subject', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='backend.subject')),
                ('tags', models.ManyToManyField(blank=True, related_name='files', to='backend.Tag')),
            ],
        ),
        migrations.AddField(
            model_name='professor',
            name='subjects',
            field=models.ManyToManyField(related_name='professors', to='backend.Subject'),
        ),
        migrations.CreateModel(
            name='AuthCode',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('code', models.CharField(max_length=50, unique=True)),
                ('authorised_datetime', models.DateTimeField(auto_now_add=True)),
                ('used_datetime', models.DateTimeField(blank=True, null=True)),
                ('purpose', models.CharField(max_length=200)),
                ('authorised_by', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, related_name='auth_codes', to='backend.professor')),
                ('used_file', models.OneToOneField(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, related_name='auth_code', to='backend.submission')),
            ],
        ),
    ]
