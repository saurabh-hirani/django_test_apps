from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib import auth
from django.core.urlresolvers import reverse
from django.core.context_processors import csrf
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse, NoReverseMatch

import test_apps.settings as settings
from test_apps.utils import anonymous_required
from test_apps.utils import render_template


@anonymous_required
def login_view(request):
    """
    Login view
    """
    context = {
        'invalid_login': False
    }
    context.update(csrf(request))
    next_url = None

    if request.POST:
        next_url = request.POST.get('next', None)
        # validate user
        username = request.POST.get('username', '')
        password = request.POST.get('password', '')
        target_app = request.POST.get('target_app', '')
        user = auth.authenticate(username=username, password=password)
        if user:
            auth.login(request, user)

            # first priority - any app that the user selected    
            if target_app != '' and target_app != 'none':
                # check if the namespace exists for this app
                try:
                    url = reverse(target_app.lower() + ':index')
                except NoReverseMatch:
                    # revert back to the login url
                    return HttpResponseRedirect(settings.USER_HOME_URL)
                else:
                    return HttpResponseRedirect(reverse(target_app.lower() + ':index'))

            # second priority - next url set
            if next_url:
                return HttpResponseRedirect(next_url)

            # no target app given - make the user choose one
            return HttpResponseRedirect(settings.USER_HOME_URL)
        else:
            # invalid user context
            context['username'] = username
            context['invalid_login'] = True
            context['next'] = next_url

    # GET request
    # check if next_url came from the query string
    next_url = next_url or request.GET.get('next', None)

    if next_url:
        # user tried accessing a page without logging in
        context['login_to_continue'] = True
    else:
        # default login request
        next_url = settings.USER_HOME_URL

    context['next'] = next_url
    return render_template(request,'test_apps/login.html', context)

@login_required
def loggedin_view(request):
    """
    What to show once the user is logged in successfully
    """
    context = {
        'full_name': request.user.username,
        'logged_in': True
    }
    return render_template(request,'test_apps/loggedin.html', context)

def logout_view(request):
    """
    Logout page
    """
    context = {}
    if request.user.is_authenticated():
        auth.logout(request)
        context['logged_out'] = True
    context.update(csrf(request))
    return render_template(request,'test_apps/login.html', context)
