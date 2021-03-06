# Generated by Django 3.1.7 on 2021-03-23 03:00

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('location', models.CharField(blank=True, choices=[('Collection', 'Collection'), ('Primary', 'Primary'), ('Secondary', 'Secondary'), ('Cure/Storate', 'Cure/Storate')], help_text='current location for pile', max_length=12)),
                ('days_at_state', models.PositiveSmallIntegerField(null=True)),
            ],
        ),
        migrations.CreateModel(
            name='Pile',
            fields=[
                ('id', models.CharField(help_text='Unique ID for a pile', max_length=20, primary_key=True, serialize=False)),
                ('born_date', models.DateField()),
                ('feedstock', models.CharField(default='horse manure', help_text='what is in this pile?  just horse S or added chips?', max_length=200)),
                ('location', models.ForeignKey(on_delete=django.db.models.deletion.RESTRICT, to='pile_tracker.location')),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('date', models.DateTimeField()),
                ('temp', models.IntegerField(blank=True, null=True)),
                ('air_temp', models.IntegerField(blank=True, null=True)),
                ('mosture_content', models.IntegerField(blank=True, null=True)),
                ('turn', models.BooleanField(default=False)),
                ('move_to', models.ForeignKey(blank=True, help_text='new location for the pile', null=True, on_delete=django.db.models.deletion.RESTRICT, to='pile_tracker.location')),
                ('pile', models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='pile_tracker.pile')),
            ],
        ),
    ]
