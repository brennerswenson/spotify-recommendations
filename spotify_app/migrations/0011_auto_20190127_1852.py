# Generated by Django 2.1.4 on 2019-01-27 18:52

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('spotify_app', '0010_recprofile_user_df_scaled_obj'),
    ]

    operations = [
        migrations.RenameField(
            model_name='recprofile',
            old_name='user_kmeans',
            new_name='user_hdbscan',
        ),
    ]
