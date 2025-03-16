from django.views.generic import View
from django.http import Http404, HttpResponseRedirect
from django.shortcuts import render
from django.urls import reverse_lazy
from django.contrib.auth.views import redirect_to_login
from web_app import models
from django.contrib.auth.mixins import LoginRequiredMixin
from core.mixins import UserMixin
from constants import SITE_TABS, SITE_VERSION

class ViewBase(View, LoginRequiredMixin, UserMixin):
    TEMPLATE_NAME = 'portal_base.html'
    TITLE = 'AI-QS - Simplified analytics for critical decision making'
    
    def get(self, request, *args, **kwargs):
        raise Http404

    def post(self, request, *args, **kwargs):
        raise Http404

    def ajax_post(self, request, *args, **kwargs):
        return self.post(request, *args, **kwargs)
    
    def ajax_get(self, request, *args, **kwargs):
        return self.get(request, *args, **kwargs)
    
    def is_permitted(self):
        permitted_urls = []
        permitted = False
        for url in self.tabs_context():
            if url['link_url'] == "#":
                for action in url['actions']:
                    if self.request.path.startswith(str(action['link_url'])):
                        permitted = True
                        break
            
            elif self.request.path.startswith(str(url['link_url'])):
                permitted = True
                break
            elif self.request.path in permitted_urls:
                permitted = True
                break
            else:
                urlFirstIndex = (str(self.request.path)).split("/")[1]
                linkFirstIndex = url['link_url'].split("/")[1]
                if urlFirstIndex == linkFirstIndex:
                    permitted = True
                    break
            
        return permitted

    def dispatch(self, request, *args, **kwargs):
        
        self.request = request
        self.args = args
        self.kwargs = kwargs
        
        if not self.user.is_authenticated:
            return redirect_to_login(request.path, reverse_lazy('login_url'))
        elif self.user.is_authenticated and self.user.is_user():
            self.redirect(reverse_lazy('user_dashboard'))
        elif self.user.is_authenticated and self.user.is_superuser():
            self.redirect(reverse_lazy('admin:index'))

        return super().dispatch(request, *args, **kwargs)
    
    def redirect(self, url):
        """Return a redirect to the given url."""
        return HttpResponseRedirect(url)

    def reverse(self, *args, **kwargs):
        """Reverse a url from it's given name & args."""
        return reverse_lazy(*args, **kwargs)


    def tabs_context(self):
        selected_tabs = []

        def getTabs(role):
            for tab in SITE_TABS:
                if role in tab['visible']:
                    if self.request.path == str(tab['link_url']):
                        tab['active'] = True
                    elif str(tab['link_url']) == "#":
                        othersTabActive = False
                        for action in tab["actions"]:
                            if self.request.path == str(action['link_url']):
                                action['active'] = True
                                othersTabActive = True
                            else:
                                action['active'] = False
                        
                        if othersTabActive:
                            tab['active'] = True
                        else:
                            tab['active'] = False
                    else:
                        tab['active'] = False
                    selected_tabs.append(tab)

        if self.request.user.is_user():
            getTabs(role="user")
        
        if self.request.user.is_superuser():
            getTabs(role="superuser")

        return selected_tabs

    def render(self, context, **kwargs):
        if self.is_permitted():
            default_context = {}
            tabs = {'tabs': self.tabs_context()}
            
            default_context.update(tabs)
            default_context.update(context)
            default_context.update({'TITLE': self.TITLE, 'SITE_VERSION': SITE_VERSION})

            return render(
                self.request,
                template_name=self.TEMPLATE_NAME,
                context=default_context,
                content_type=kwargs.get('content_type', None)
            )
        return self.redirect('/')