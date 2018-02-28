# Generated by Django 2.0.2 on 2018-02-28 22:39

from django.db import migrations, models


class Migration(migrations.Migration):

    initial = True

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='ShortUrl',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('created_at', models.DateTimeField(verbose_name='created_at')),
                ('target_url_desktop', models.URLField(null=True)),
                ('desktop_redirects', models.IntegerField(default=0)),
                ('target_url_tablet', models.URLField(null=True)),
                ('tablet_redirects', models.IntegerField(default=0)),
                ('target_url_mobile', models.URLField(null=True)),
                ('mobile_redirects', models.IntegerField(default=0)),
            ],
        ),
    ]
