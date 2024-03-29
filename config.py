class SubdomainMiddleware:
    def process_request(self, request):
        """Parsing the subdomain from the request"""
        request.subdomain = None
        host = request.META.get('HTTP_HOST', '')
        host_s = host.lower().replace('www.', '').split('.')
        if len(host_s) > 2:
            request.subdomain = ''.join(host_s[:-2])