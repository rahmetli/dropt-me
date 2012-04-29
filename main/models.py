from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

class UserProfile(models.Model):
    user = models.OneToOneField(User)
    #requestToken = models.CharField(blank=True, null=True, unique=True)
    #accessToken = models.CharField(blank=True, null=True)
    #dropboxID = models.CharField(blank=True, null=True, unique=True)

    def is_connected(self):
        try:
            self.user.dropboxaccount_set.get()
            return True
        except:
            return False


def create_user_profile(sender, instance, created, **kwargs):
    if created:
        UserProfile.objects.create(user=instance)

post_save.connect(create_user_profile, sender=User)