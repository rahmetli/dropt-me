from django.http import HttpResponseRedirect, HttpResponse, Http404
from django.shortcuts import get_object_or_404, render_to_response
from django.template import RequestContext
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from django.conf import settings

from os import path

from main.forms import RegisterForm, LoginForm
from account.views import handle_single_link, handle_complete_link, handle_directory_change, show_account_page, authorize_account, try_to_connect_or_delete

def url_dispatcher(request):
	url = get_url(request.META.get('PATH_INFO'))

	# if it's a subdomain
	if request.subdomain:
		# check subdomain's existance
		try:
			User.objects.get(username__exact = request.subdomain)
		except User.DoesNotExist:
			raise Http404 # this subdomain is not in database
		# just one extra valid segment
		if is_single_segment(url):
			if url[0] == 'logout':
				return logout_view(request)
			elif url[0] == "handle_directory_change":
				return handle_directory_change(request)
			else:
				return handle_single_link(request, url) # redirection
		elif is_url_valid(url):
			return handle_complete_link(request, url) # redirection
		else:
			#default user page
			return show_account_page(request)

		raise Http404
	else:
		# just one extra valid segment
		if is_single_segment(url):
			# supported links for main page
			if url[0] == 'login':
				return login_view(request)
			elif url[0] == 'register':
				return register_view(request)
			elif url[0] == 'success':
				return success_view(request)
			elif url[0] == 'logout':
				return logout_view(request)
			elif url[0] == 'authorize':
				return authorize_account(request)
			else:
				raise Http404

	# default page
	return index_view(request)

def get_url(url):
	""" get the segments of domain in www.domain.com/seg1/seg2... """
	list = url.split('/')
	return list[1:]

def is_single_segment(url):
	""" check if there is only segment in www.domain.com/segmet/ """
	if (len(url) == 2 and url[1] == '') or (len(url) == 1 and url[0] != ''):
		return True
	else:
		return False

def is_url_valid(url):
	""" check if any of multiple segments is empty or not """
	if url[0] == '' or len(url) < 2:
		return False
	else:
		for i in range(len(url)-1):
			if url[i] == '':
				return False
		return True


def index_view(request):
	if request.subdomain:
		return render_to_response(
						'common/base.html', None,
						context_instance=RequestContext(request))
	else:
		return render_to_response(
						'common/base.html', None,
						context_instance=RequestContext(request))

def login_view(request):
	redirect_url = request.GET.get('next', '/')
	# login is submitted
	if request.method == 'POST':
		# create form from request
		form = LoginForm(redirect_url, request.POST)
		# regular form validation
		if form.is_valid():
			# create instances
			u = form.cleaned_data['username']
			p = form.cleaned_data['password']
			user = authenticate(username=u, password=p)

			# information check
			if(user is not None):
				login(request, user)
				#url = settings.SITE_URL.replace('www', u) # create url
				try_to_connect_or_delete(request)
				return HttpResponseRedirect(form.cleaned_data['redirect'])
			else:
				form.errors['username'] = [u'User and password does not match!']
				return render_to_response(
								'register/login.html', {'form' : form},
								context_instance=RequestContext(request))
		# form is not valid
		else:
			return render_to_response(
							'register/login.html', {'form' : form},
							context_instance=RequestContext(request))
	
	form = LoginForm(redirect_url)
	return render_to_response(
					'register/login.html', {'form' : form},
					context_instance=RequestContext(request))


def logout_view(request):
	if settings.DROPBOX_SESSION.is_linked():
		settings.DROPBOX_SESSION.unlink()
		settings.DROPBOX_TOKEN = None
	logout(request)
	return HttpResponseRedirect('/')

def register_view(request):
	# register is submitted
	if request.method == 'POST':
		form = RegisterForm(request.POST)
		if(form.is_valid()):
			# create instances
			u = form.cleaned_data['username']
			email = form.cleaned_data['email']
			p1 = form.cleaned_data['password']
			p2 = form.cleaned_data['pwrepeat']
			
			# wrong password
			if p1 != p2:
				form.errors['password'] = [u'Passwords do not match']
				return render_to_response(
								'register/register.html', {'form' : form},
								context_instance=RequestContext(request))
			else:
				user = User.objects.create_user(u, email, p1)
				return HttpResponseRedirect('/register?success=1')
		else:
			return render_to_response(
							'register/register.html', {'form' : form},
							context_instance=RequestContext(request))

	if request.GET.get('success', ''):
		message = 'Your account has been succesfuly created.'
	else:
		message = None

	form = RegisterForm()
	return render_to_response(
					'register/register.html', {'form' : form, 'message' : message},
					context_instance=RequestContext(request))