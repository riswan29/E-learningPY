# Generated by Django 4.2.5 on 2023-10-05 22:47

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('app', '0009_alter_jadwalmengajar_hari'),
    ]

    operations = [
        migrations.AlterField(
            model_name='jadwalmengajar',
            name='hari',
            field=models.CharField(choices=[('MONDAY', 'SENIN'), ('TUESDAY', 'SELASA'), ('WEDNESDAY', 'RABU'), ('THURSDAY', 'KAMIS'), ('FRIDAY', 'JUMAT'), ('SATURDAY', 'SABTU')], max_length=100),
        ),
    ]
