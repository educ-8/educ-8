# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('main', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='CommunityMember',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('ig_username', models.CharField(max_length=255, blank=True)),
                ('ig_user_id', models.CharField(max_length=100, blank=True)),
                ('twitter_name', models.CharField(max_length=255, blank=True)),
                ('twitter_handle', models.CharField(max_length=255, blank=True)),
                ('twitter_user_id', models.CharField(max_length=100, blank=True)),
                ('school', models.ForeignKey(to='main.School')),
            ],
        ),
        migrations.CreateModel(
            name='Hashtag',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('text', models.CharField(max_length=255)),
            ],
        ),
        migrations.CreateModel(
            name='HashtagUse',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('hashtag', models.ForeignKey(to='main.Hashtag')),
            ],
        ),
        migrations.CreateModel(
            name='Post',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('post_id', models.CharField(max_length=50)),
                ('user_id', models.CharField(max_length=50)),
                ('datetime', models.DateTimeField()),
            ],
        ),
        migrations.CreateModel(
            name='SchoolNickname',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
                ('school', models.ForeignKey(to='main.School')),
            ],
        ),
        migrations.CreateModel(
            name='SocialNetwork',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('name', models.CharField(max_length=255)),
            ],
        ),
        migrations.AddField(
            model_name='post',
            name='source',
            field=models.ForeignKey(to='main.SocialNetwork'),
        ),
        migrations.AddField(
            model_name='hashtaguse',
            name='post',
            field=models.ForeignKey(to='main.Post'),
        ),
        migrations.AddField(
            model_name='hashtaguse',
            name='school',
            field=models.ForeignKey(to='main.School'),
        ),
        migrations.AddField(
            model_name='school',
            name='hashtags',
            field=models.ManyToManyField(to='main.Hashtag', through='main.HashtagUse'),
        ),
        migrations.AddField(
            model_name='school',
            name='posts',
            field=models.ManyToManyField(to='main.Post'),
        ),
    ]
