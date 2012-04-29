from django import forms
from django.contrib.auth.models import User

class RegisterForm(forms.Form):
	username = forms.CharField(label='username', error_messages={'required' : 'Username is required'})
	email = forms.EmailField(label='e-mail', error_messages={'required' : 'Email is required'})
	password = forms.CharField(label='password', error_messages={'required' : 'Password is required'}, widget=forms.PasswordInput)
	pwrepeat = forms.CharField(label='again', error_messages={'required' : 'Repeat your password'}, widget=forms.PasswordInput)
	
	def clean_username(self):
		user = self.cleaned_data['username']
		if user:
			try:
				User.objects.get(username__exact = user)
				raise forms.ValidationError("The username is already in use")
			except User.DoesNotExist:
				return user
		return user

class LoginForm(forms.Form):
	username = forms.CharField(label='username', error_messages={'required' : 'Username is required'})
	password = forms.CharField(label='password', error_messages={'required' : 'Password is required'}, widget=forms.PasswordInput)
	redirect = forms.CharField(widget=forms.HiddenInput)

	def __init__(self, url, *args, **kwargs):
		super(LoginForm, self).__init__(*args, **kwargs)
		self.fields['redirect'].initial = url