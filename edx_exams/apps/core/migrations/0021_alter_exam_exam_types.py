# Generated by Django 3.2.23 on 2023-12-07 14:33

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0020_auto_20231010_1442'),
    ]

    operations = [
        migrations.AlterField(
            model_name='exam',
            name='exam_type',
            field=models.CharField(choices=[('onboarding', 'onboarding'), ('practice', 'practice'), ('proctored', 'proctored'), ('timed', 'timed')], db_index=True, max_length=255),
        ),
        migrations.AlterField(
            model_name='historicalexam',
            name='exam_type',
            field=models.CharField(choices=[('onboarding', 'onboarding'), ('practice', 'practice'), ('proctored', 'proctored'), ('timed', 'timed')], db_index=True, max_length=255),
        ),
    ]