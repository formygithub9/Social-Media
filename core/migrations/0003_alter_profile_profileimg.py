# Generated by Django 4.1.3 on 2023-06-20 09:57

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('core', '0002_alter_profile_location'),
    ]

    operations = [
        migrations.AlterField(
            model_name='profile',
            name='profileimg',
            field=models.ImageField(default='static/images/blank-profile-picture.jpeg', upload_to='Page_images/profile-pics'),
        ),
    ]
