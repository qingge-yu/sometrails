# Generated by Django 4.1.2 on 2022-10-31 18:24

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main_app', '0005_alter_review_rating_photo'),
    ]

    operations = [
        migrations.RenameField(
            model_name='photo',
            old_name='cat',
            new_name='hike',
        ),
    ]
