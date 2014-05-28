"""
Utility functions used in the project
"""
from django.template import RequestContext
from django.utils import timezone
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.models import User
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.shortcuts import get_object_or_404
from functools import wraps

import test_apps.settings as settings
from polls.models import Poll, Choice
import datetime
import importlib

MAX_TESTUSER_COUNT = 10



def create_user(username=None, password=None, email=None):
    """
    Create user
    """
    if username is None:
        username = 'testuser'
    if password is None:
        password = username 
    if email is None:
        email = 'test@test.com'
    return User.objects.create_user(username, email, password)

def create_users(user_info = None, prefix='testuser', count=5):
    """
    Create a bunch of test users
    """
    if user_info:
        count = len(user_info)

    if count > MAX_TESTUSER_COUNT:
        raise ValueError('Cannot create more than %d users' % MAX_TESTUSER_COUNT)

    for i in range(1, count + 1):
        # get current user info if provided:
        curr_user = {}
        if user_info:
            curr_user = user_info[i - 1]

        username = curr_user.get('username', prefix + str(i))

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            email = curr_user.get('email', '%s@%s.com'% (username, username))
            password = curr_user.get('password', username)
            user = create_user(username=username, email=email, password=password)
        finally:
            yield user

def delete_user(user):
    """
    Delete user
    """
    return user.delete() 

def delete_users(user_info = None, prefix='testuser', count=5):
    """
    Delete the created test users
    """
    if user_info:
        count = len(user_info)

    if count > MAX_TESTUSER_COUNT:
        raise ValueError('Cannot delete more than %d users' % MAX_TESTUSER_COUNT)

    for i in range(1, count + 1):
        # get current user info if provided:
        curr_user = {}
        if user_info:
            curr_user = user_info[i - 1]

        username = curr_user.get('username', prefix + str(i))

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            pass
        else:
            username = user.username
            delete_user(user)
            yield username

def create_poll(question, days):
    """
    Create a poll
    """
    return Poll.objects.create(question=question,  
                               pub_date = timezone.now() + \
                               datetime.timedelta(days=days))

def add_poll_choices(poll, choices):
    """ 
    Add a choices to an existing poll
    """
    for choice in choices:
        yield Choice.objects.create(poll_id = poll.id, 
                                    choice_text = choice['name'], 
                                    votes = choice['votes'])

def add_default_choices(poll):
    """
    Add default choices to an existing poll
    """
    choices = [
        { 'name': 'choice1', 'votes': 0 },
        { 'name': 'choice2', 'votes': 0 },
        { 'name': 'choice3', 'votes': 0 },
    ]
    return list(add_poll_choices(poll, choices))

def create_default_poll():
    """
    Create poll with default question and default choices
    """
    poll = create_poll(question='test question', days=-5)
    add_default_choices(poll)
    return poll


class TestCaseWithUtils(TestCase):
    """
    TestCase wrapper class with helper methods
    """
    @staticmethod
    def create_test_user(username=None):
        if username is None:
            return create_user()
        return create_user()

    @staticmethod
    def create_test_poll():
        return create_default_poll()

    def login(self):
        self.client.login(username=self.user.username, password=self.user.username)

    def post(self, reverse_url, *url_args, **kwargs):
        self.client.post(reverse('polls:' + reverse_url, args=url_args), kwargs)
        
    def logout(self):
        self.client.logout()

class LoginMixin():
    """
    Mixin to add login/logout functionality to tests
    """
    def setUp(self):
        self.user = create_user()
        self.client.login(username=self.user.username, password=self.user.username)

    def tearDown(self):
        self.client.logout()
        delete_user(self.user)

def is_user_logged_in(client, user=None):
    """
    Check if user is logged in
    """
    has_user_id_key = '_auth_user_id' in client.session.keys()
    if not has_user_id_key: 
        return False
    if user is None:
        return True
    return client.session['_auth_user_id'] == user.pk


def get_app_preview_ctx(app_name):
    """
    Return preview context for specific app
    """
    try:
        app_view = importlib.import_module('%s.views' % app_name)
    except ImportError:    
        return {}
    return app_view.get_preview_context()

def get_target_apps():
    """
    Return list of target apps
    """
    return [ 
        {
            'name': 'polls',
            'url': 'polls:index',
            'caption': 'Polls',
            'preview_ctx': get_app_preview_ctx('polls')
        },
        {
            'name': 'blogs',
            'url': 'blogs:index',
            'caption': 'Blogs',
            'preview_ctx': get_app_preview_ctx('polls')
        }
    ]

def required_voting_status(req_status = True):
    """
    Function to decorate voting_status
    """
    def decorator(view_func):
        @wraps(view_func)
        def view_wrapper(request, *args, **kwargs):
            #print "------- voting status check --------"
            queryset = Poll.objects.filter(pub_date__lte=timezone.now())
            poll_id = kwargs['poll_id']
            poll = get_object_or_404(queryset, pk=poll_id)
            voter = poll.voter_set.get(user=request.user)

            if req_status is True:
                #print "----------- voter should have voted ------------"
                if voter.has_voted is False:
                    #print "----------- voter has not voted ------------"
                    return HttpResponseRedirect(reverse('polls:index'))
                #print "----------- voter has voted ------------"
            else:
                #print "----------- voter should not have voted ------------"
                if voter.has_voted:
                    #print "----------- voter has voted ------------"
                    return HttpResponseRedirect(reverse('polls:results', args=(poll.id,)))
                #print "----------- voter has not voted ------------"
            kwargs['poll'] = poll
            kwargs['voter'] = voter
            return view_func(request, *args, **kwargs)
        return view_wrapper
    return decorator
 
def required_poll_status(req_status = True):
    """
    Function to decorate poll status
    """
    def decorator(view_func):
        @wraps(view_func)
        def view_wrapper(request, *args, **kwargs):
            #print "------- poll status check --------"
            queryset = Poll.objects.filter(pub_date__lte=timezone.now())
            poll_id = None
            if 'poll_id' in kwargs:
                poll_id = kwargs['poll_id']
            poll = get_object_or_404(queryset, pk=poll_id)

            if req_status is True:
                #print "-------- poll should be open ----------"
                if poll.is_open is False:
                    #print "-------- poll is not open ----------"
                    return HttpResponseRedirect(reverse('polls:results', args=(poll.id,)))
                #print "-------- poll is open ----------"
            else:
                #print "-------- poll should not be open ----------"
                if poll.is_open:
                    #print "-------- poll is open ----------"
                    return HttpResponseRedirect(reverse('polls:index'))
                #print "--------- poll is not open --------"
            kwargs['poll'] = poll
            return view_func(request, *args, **kwargs)
        return view_wrapper
    return decorator
            
def anonymous_required(view_func):
    """
    Decorator to ensure that user is not logged in
    """
    @wraps(view_func)
    def view_wrapper(request, *args, **kwargs):
        """
        poll_open_required wrapper
        """
        if request.user.is_authenticated():
            return HttpResponseRedirect(settings.USER_HOME_URL)
        return view_func(request, *args, **kwargs)
    return view_wrapper


def render_template(request, template, context=None):
    """
    Shortcut to include RequestContext
    """
    context_instance = RequestContext(request,
                                      {'target_apps': get_target_apps()})
    response = render_to_response(template, context, context_instance=context_instance)
    return response
