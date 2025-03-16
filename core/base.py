from django.views.generic import View
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from core.mixins import UserMixin
from constants import SITE_VERSION
from django.contrib.auth.signals import user_logged_in
from web_app import models

class ViewBase(View, LoginRequiredMixin, UserMixin):
    TEMPLATE_NAME = 'base.html'
    TITLE = 'AI-QS - Simplified analytics for critical decision making'
    
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        raise Http404

    def ajax_post(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def ajax_get(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)

    def dispatch(self, request, *args, **kwargs):
        
        self.request = request
        self.args = args
        self.kwargs = kwargs

        return super().dispatch(request, *args, **kwargs)
    
    def redirect(self, url):
        """Return a redirect to the given url."""
        return HttpResponseRedirect(url)

    def reverse(self, *args, **kwargs):
        """Reverse a url from it's given name & args."""
        return reverse_lazy(*args, **kwargs)

    def user_logged_in_handler(sender, request, user, **kwargs):
        models.UserSession.objects.get_or_create(user = user, session_id = request.session.session_key)
        session = models.UserSession.objects.filter(user=request.user)
        for data in session:
            if request.session.session_key != data.session.session_key:
                data.session.delete()

    def render(self, context, **kwargs):
        default_context = {}
        default_context.update(context)
        default_context.update({'TITLE': self.TITLE, 'SITE_VERSION': SITE_VERSION})
        return render(
            self.request,
            template_name=self.TEMPLATE_NAME,
            context=default_context,
            content_type=kwargs.get('content_type', None)
        )

    user_logged_in.connect(user_logged_in_handler)