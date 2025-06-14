import logging
from core.base import ViewBase
from django.contrib.auth import logout
from django.urls import reverse_lazy

logger = logging.getLogger(__name__)


class landingView(ViewBase):
    TEMPLATE_NAME = 'landing/landing.html'

    def get(self, request, *args, **kwargs):
        logout(request)

        return self.redirect(reverse_lazy('login_url'))
    
        context = {
            'nav': 'home',
        }

        return self.render(context)
    

class contactView(ViewBase):
    TEMPLATE_NAME = 'landing/contact.html'

    def get(self, request, *args, **kwargs):

        logout(request)

        return self.redirect(reverse_lazy('login_url'))
    
        context = {}

        return self.render(context)