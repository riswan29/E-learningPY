# Generated by Django 4.2.5 on 2023-09-25 17:21

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chatbot', '0002_sesichat_name'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='sesichat',
            name='name',
        ),
    ]