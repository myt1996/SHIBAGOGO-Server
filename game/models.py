from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class APPUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, related_name="app_user")
    info = models.IntegerField(default=0)
    image = models.CharField(max_length=30, default="Data/no_image.png")
    token = models.CharField(max_length=50, default="NoneUser")

    def __str__(self):
        return "user{}".format(self.user.username)

class Pet(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=30, default="Pet")
    level = models.IntegerField(default=1)
    status = models.CharField(max_length=100, default="Normal")

    def __str__(self):
        return "{}_pet{}".format(self.user, self.name)

class Friend(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="friend_start_user")
    friend = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="friend_end_user")

    def __str__(self):
        return "{}_and_{}_friend".format(self.user, self.friend)

class Place(models.Model):
    x = models.FloatField(default=0)
    y = models.FloatField(default=0)
    name = models.CharField(max_length=50, default="NonePlace")
    type = models.IntegerField(default=-1)

class Quest(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, default=None, related_name="quest_user")
    place = models.ForeignKey(Place, on_delete=models.CASCADE, default=None, related_name="quest_place")
    start = models.DateTimeField()
    end = models.DateTimeField()
    status = models.IntegerField(default=-1)
    info = models.CharField(max_length=50, default="NoneQuest")