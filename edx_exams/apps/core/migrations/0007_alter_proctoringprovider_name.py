# Generated by Django 3.2.14 on 2022-07-28 14:16

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0006_alter_courseexamconfiguration_course_id'),
    ]

    operations = [
        migrations.AlterField(
            model_name='proctoringprovider',
            name='name',
            field=models.CharField(db_index=True, max_length=255, unique=True),
        ),
    ]
