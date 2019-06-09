from django.db import models
from django.contrib.auth.models import User

# Create your models here.

class APPUser(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, default=None, related_name="app_user")
    qr = models.CharField(max_length=30, default="Data/no_qr.png")

    def __str__(self):
        return "user{}".format(self.user.username)

class Pet(models.Model):
    user = models.ForeignKey(APPUser, on_delete=models.CASCADE, default=None)
    name = models.CharField(max_length=30, default="Pet")
    level = models.IntegerField(default=1)
    status = models.CharField(max_length=100, default="Normal")

    def __str__(self):
        return "{}_pet{}".format(self.user, self.name)