# Generated by Django 3.1.7 on 2021-03-24 00:06

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('pile_tracker', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='log',
            name='notes',
            field=models.CharField(blank=True, help_text='general notes', max_length=200, null=True),
        ),
    ]
