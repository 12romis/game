# Generated by Django 2.0.2 on 2018-02-13 13:11

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('game', '0003_auto_20180213_1200'),
    ]

    operations = [
        migrations.RenameField(
            model_name='profile',
            old_name='attempts_user',
            new_name='attempts_used',
        ),
        migrations.AlterField(
            model_name='profile',
            name='token',
            field=models.CharField(default='CCoK58RIJ40MX6vDT9GvUMiZ9TfaT1gw', max_length=100),
        ),
    ]
