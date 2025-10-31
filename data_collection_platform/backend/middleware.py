from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils.deprecation import MiddlewareMixin

class JWTAuthMiddleware(MiddlewareMixin):
    def __init__(self, get_response=None):
        super().__init__(get_response)
        self.auth = JWTAuthentication()
    def __call__(self, request):
        header = request.META.get('HTTP_AUTHORIZATION', '')
        if header.startswith('Bearer '):
            try:
                user_auth = self.auth.authenticate(request)
                if user_auth:
                    request.user, request.auth = user_auth
            except Exception:
                pass
        return self.get_response(request)
