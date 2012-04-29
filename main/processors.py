from django.conf import settings
def constants(request):
    context = {
    	'SITE_URL': settings.SITE_URL,
    	'SITE_ROOT': settings.SITE_ROOT,
    }
    return context