from django.db import models
from django.contrib.auth.models import User

# Create your models here.
class DropboxAccount(models.Model):
	user = models.ForeignKey(User, unique=True)
	dropbox_id = models.CharField(max_length=200, blank=True, null=True, unique=True)
	oauth_token = models.CharField(max_length=200, blank=True, null=True, unique=True)
	oauth_secret = models.CharField(max_length=200, blank=True, null=True, unique=True)
	public = models.BooleanField(blank=False, null=False, default=False)

class Shared(models.Model):
	dropbox = models.ForeignKey(DropboxAccount)
	path = models.CharField(max_length=400, blank=False, null=False)
	shortcut_link = models.CharField(max_length=200, blank=True, null=True)
	is_dir = models.CharField(max_length=200, blank=False, null=False)
	click_count = models.IntegerField(blank=True, null=False, default = '0')
	public = models.BooleanField(blank=False, null=False, default=True)
	date_created = models.DateField(auto_now_add = True)
	last_visited = models.DateField(auto_now_add = True)