# Generated by Django 3.2.13 on 2022-06-23 13:19

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0004_alter_exam_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='lms_user_id',
            field=models.IntegerField(db_index=True, null=True),
        ),
    ]
