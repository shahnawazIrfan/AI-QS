from django.conf import settings
from django.contrib.auth import get_user_model, backends
from django.db.models import Q

class EmailModelBackend(backends.BaseBackend):
    """  Authenticate User with Email """
    USER_MODEL = get_user_model()


    def authenticate(self, request, **kwargs):
        custom_kwargs = {}
        username = kwargs.get("username")
        password = kwargs.get("password")
        
        custom_kwargs = Q(email=username.lower())
        
        try:
            user = self.USER_MODEL.objects.filter(custom_kwargs)
        except self.USER_MODEL.DoesNotExist:
            return None
        for index in user:
            if index.check_password(password) and index.is_active:
                return index
        
        return None
    
    def get_user(self, user_id):
        try:
            return self.USER_MODEL.objects.get(pk=user_id)
        except self.USER_MODEL.DoesNotExist:
            return None