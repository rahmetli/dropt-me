from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth.models import User
from django.contrib.auth.decorators import login_required
from django.views.decorators.csrf import csrf_exempt
from django.conf import settings
from operator import itemgetter

from dropbox import client, session
import sys

def handle_single_link(request):
	pass

def handle_complete_link(request):
	pass

def handle_directory_change(request):
	if is_owner(request.subdomain, request.user.username):
		username = request.subdomain
		path = request.POST['path']
		c = get_client(username)
		directory = get_directory(c, path)
		return render_to_response(
						"ajax/directory.html", {'directory' : directory['directory'], 'path' : directory['current_path']},
						context_instance = RequestContext(request))


def show_account_page(request):
	subdomain = request.subdomain
	subuser = User.objects.get(username__exact = subdomain)
	subuserP = User.get_profile(subuser)

	if is_owner(subdomain, request.user.username):
		return render_to_response('user/user.html', {'directory': 'given'}, context_instance = RequestContext(request))
	else:
		return render_to_response('user/user.html', None, context_instance = RequestContext(request))

	"""
	if c:
		if is_owner(subdomain, request.user.username):
			directory = get_directory(c, '/Public/')
			return render_to_response('user/user.html', {'directory' : directory['directory'], 'path' : directory['current_path']}, context_instance = RequestContext(request))
		else:
			
	else:
		return render_to_response('user/user.html', None, context_instance = RequestContext(request))
	"""
		

def get_directory(client, current_path = "/"):
	list = client.metadata(current_path, list=True, file_limit=10000, hash=None, rev=None, include_deleted=False)
	info = []
	for content in list['contents']:
		path = content['path'].split(current_path)[1:]
		path = ''.join(path)
		is_dir = content['is_dir']
		insert = {'path' : path, 'is_dir' : is_dir}
		info.append(insert)
	info = sorted(info, key = itemgetter('is_dir'), reverse=True) # sort by type
	data = {'directory' : info, 'current_path' : current_path}
	return data

def is_owner(subdomain, username):
	if(subdomain == username):
		return True
	else:
		return False

@login_required
def authorize_account(request):
	username = request.user.username
	user = User.objects.get(username__exact = username)
	userP = User.get_profile(user)
	if userP.is_connected():
		d = user.dropboxaccount_set.get()
		if get_client(username):
			print 'user already has an account token, token: ', d.oauth_token, ' secret: ', d.oauth_secret
			return render_to_response(
							"user/authorize.html", {'registered' : d.dropbox_id},
							context_instance = RequestContext(request))
		else:
			d.delete()
			if settings.DROPBOX_SESSION.is_linked():
				settings.DROPBOX_SESSION.unlink()
			settings.DROPBOX_TOKEN = None
			return HttpResponseRedirect('/authorize/')
	else:
		if settings.DROPBOX_TOKEN:
			print 'There is a token waiting to be accessed token: ', settings.DROPBOX_TOKEN.key, ' secret: ', settings.DROPBOX_TOKEN.secret
			try:
				print 'Trying to get access token'
				access_token = settings.DROPBOX_SESSION.obtain_access_token(settings.DROPBOX_TOKEN)
				print 'Access gathered token: ', access_token.key, ' secret: ', access_token.secret
				settings.DROPBOX_SESSION.set_token(access_token.key, access_token.secret)
				print 'Key is set to the session'
				c = client.DropboxClient(settings.DROPBOX_SESSION)
				print 'Client is created with id ', c.account_info()['uid']
				user.dropboxaccount_set.create(dropbox_id = c.account_info()['uid'], oauth_token = access_token.key, oauth_secret = access_token.secret)
				print 'User connection is created'
			except:
				print 'error: ', sys.exc_info()[0]
				settings.DROPBOX_TOKEN = None
				print 'Access has failed, redirecting'
				return HttpResponseRedirect('/authorize/')
			else:
				return HttpResponseRedirect('/authorize/')
		else:

			settings.DROPBOX_TOKEN = settings.DROPBOX_SESSION.obtain_request_token()
			print 'Token is created, token :', settings.DROPBOX_TOKEN.key, ' secret: ', settings.DROPBOX_TOKEN.secret
			callback_url = settings.SITE_URL + '/authorize/'
			url = settings.DROPBOX_SESSION.build_authorize_url(settings.DROPBOX_TOKEN, oauth_callback=callback_url)
			return render_to_response(
							"user/authorize.html", {'direct' : url},
							context_instance = RequestContext(request))

def get_client(username):
	user = User.objects.get(username__exact = username)
	try:
		d = user.dropboxaccount_set.get()
	except:
		return None

	try:
		if settings.DROPBOX_SESSION.is_linked():
			settings.DROPBOX_SESSION.unlink()
		settings.DROPBOX_SESSION.set_token(d.oauth_token, d.oauth_secret)
		c = client.DropboxClient(settings.DROPBOX_SESSION)
		print c.account_info()
		return c
	except:
		d.delete()
		return None


def try_to_connect_or_delete(request):
	username = request.user.username
	if username:
		user = User.objects.get(username__exact = username)
		userP = User.get_profile(user)
		if userP.is_connected():
			d = user.dropboxaccount_set.get()
			if settings.DROPBOX_SESSION.is_linked():
				settings.DROPBOX_SESSION.unlink()
			settings.DROPBOX_SESSION.set_token(d.oauth_token, d.oauth_secret)
			try:
				client.DropboxClient(settings.DROPBOX_SESSION).account_info()
				return True
			except:
				d.delete()
				return False
		else:
			return False
	else:
		return False
