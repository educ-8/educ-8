from django.db import models

# add Models here

# School
# id
# full_name
# lat
# lng
# fb_places_id
class SocialNetwork(models.Model):
    name = models.CharField(max_length=255)

class Post(models.Model):
    source = models.ForeignKey(SocialNetwork)
    post_id = models.CharField(max_length=50)
    user_id = models.CharField(max_length=50)
    datetime = models.DateTimeField()

class Hashtag(models.Model):
    text = models.CharField(max_length=255)

class School(models.Model):
    name = models.CharField(max_length=255)
    lat = models.FloatField()
    lng = models.FloatField()
    posts = models.ManyToManyField(Post)
    hashtags = models.ManyToManyField(Hashtag, through="HashtagUse")

class SchoolNickname(models.Model):
    name = models.CharField(max_length=255)
    school = models.ForeignKey(School)

class CommunityMember(models.Model):
    ig_username = models.CharField(max_length=255, blank=True)
    ig_user_id = models.CharField(max_length=100, blank=True)
    twitter_name = models.CharField(max_length=255, blank=True)
    twitter_handle = models.CharField(max_length=255, blank=True)
    twitter_user_id = models.CharField(max_length=100, blank=True)
    school = models.ForeignKey(School)

class HashtagUse(models.Model):
    hashtag = models.ForeignKey(Hashtag)
    school = models.ForeignKey(School)
    post = models.ForeignKey(Post)
