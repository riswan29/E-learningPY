# Generated by Django 4.2.5 on 2023-09-26 00:50

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0003_rename_courseschedule_jadwalmengajar'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jadwalmengajar',
            name='metode_pembelajaran',
            field=models.CharField(choices=[('Luring', 'Luring'), ('Daring', 'Daring')], max_length=100),
        ),
    ]