from django.contrib.auth.views import LoginView
import requests


class CustomLoginView(LoginView):
    template_name = 'accounts/login.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        client_ip = self.get_client_ip(self.request)
        context.update(self.get_location_from_ip(client_ip))
        return context

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def get_location_from_ip(self, ip):
        url = f"https://ipinfo.io/{ip}/json"
        r = requests.get(url)

        if r.status_code == 200:
            data = r.json()
        else:
            data = data.get('error', None)

        return {
            'sucess': r.status_code == 200,
            'bogon': data.get('bogon', False),
            'loc': data.get('loc', '-33.0498108,-71.6213084')
        }

