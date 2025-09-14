from rest_framework import authentication
from rest_framework.exceptions import AuthenticationFailed
from .models import Device

class TokenAuthentication(authentication.BaseAuthentication):
    def authenticate(self, request):
        auth_header = request.headers.get('Authorization')
        if not auth_header:
            return None

        try:
            token_prefix, token_key = auth_header.split()
            if token_prefix.lower() != 'token':
                return None
        except ValueError:
            return None

        try:
            device = Device.objects.get(token=token_key)
        except Device.DoesNotExist:
            raise AuthenticationFailed('Token inválido')

        return (device, None)