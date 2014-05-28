"""
Test class for polls
"""
import datetime

from django.utils import timezone
from django.test import TestCase
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User
from django.test.utils import setup_test_environment
setup_test_environment()

import test_apps.utils as utils

VALID_CREDS = {
    'username': 'testuser',
    'password': 'testuser'
}

LOGIN_URL = reverse('login_view')
LOGGEDIN_URL = reverse('loggedin_view')
LOGOUT_URL = reverse('logout_view')

class UtilsTest(TestCase):
    """
    Test the utils package
    """
    def test_get_app_preview_ctx(self):
        """
        Test get_app_preview_ctx
        """
        preview_data = utils.get_app_preview_ctx('something')
        self.assertEqual(len(preview_data.keys()), 0)
        preview_data = utils.get_app_preview_ctx('polls')
        self.assertTrue(len(preview_data.keys()) > 0)

    def test_create_delete_users(self):
        user_info = [
            {'username': 'u1', 'email': 'u1@u1.com', 'password': 'u1'},
            {'username': 'u2', 'email': 'u2@u2.com', 'password': 'u2'},
        ]
        list(utils.create_users(user_info))
        list(utils.create_users())

class LoginViewTest(TestCase):
    """
    Test the login page
    """
    def test_login_page_available(self):
        """
        Just check if we can access the view url
        """
        response = self.client.get(reverse('login_view'))
        self.assertEqual(response.status_code, 200) 

    def test_login_invalid(self):
        """
        Access the view with invalid credentials
        """
        # no credentials
        response = self.client.post(reverse('login_view'), {'username': '',
                                                            'password': ''})
        self.assertContains(response, 'Failed to login')

        # invalid username
        response = self.client.post(reverse('login_view'), {'username': 'testuser1234'})
        self.assertContains(response, 'Failed to login')

        ## valid username - no passwd
        response = self.client.post(reverse('login_view'), {'username': 'testuser'})
        self.assertContains(response, 'Failed to login')

        ## valid username - invalid passwd
        response = self.client.post(reverse('login_view'), {'username': 'testuser',
                                                            'password': '1234'})
        self.assertContains(response, 'Failed to login')

class ValidLoginViewTest(utils.TestCaseWithUtils):
    """
    Test valid login view
    """
    @classmethod
    def setUpClass(cls):
        cls.user = utils.create_user()

    @classmethod
    def tearDownClass(cls):
        utils.delete_user(cls.user)

    def tearDown(self):
        self.client.get(LOGOUT_URL)
     
    def test_basic_login(self):
        """
        Test basic login functionality
        """
        # check if user logged in and redirected to the right url
        response = self.client.post(LOGIN_URL, VALID_CREDS)
        self.assertTrue(utils.is_user_logged_in(self.client, self.user))
        self.assertEqual(response.status_code, 302)
        self.assertTrue(LOGGEDIN_URL in response['Location'])

    def test_basic_login_follow_url(self):
        """
        Follow the redirected url to confirm
        """
        # relogin - this time follow the redirected url
        response = self.client.post(LOGIN_URL, VALID_CREDS, follow=True)
        self.assertEqual(response.status_code, 200)
    
    def test_login_w_invalid_target_app(self):
        """
        Specify invalid target app during login
        """
        post_data = dict(VALID_CREDS)
        # relogin - this time with invalid target app
        post_data['target_app'] = 'polls_apart'
        response = self.client.post(LOGIN_URL, post_data)
        # check whether user redirected to the home url
        self.assertEqual(response.status_code, 302)
        self.assertTrue(LOGGEDIN_URL in response['Location'])

    def test_login_w_valid_target_app(self):
        """
        Specify valid target app during login
        """
        # relogin - this time with valid target_app set
        post_data = dict(VALID_CREDS)
        post_data['target_app'] = 'polls'
        response = self.client.post(LOGIN_URL, post_data)
        # check whether user redirected to target_app
        self.assertEqual(response.status_code, 302)
        self.assertTrue(reverse('polls:index') in response['Location'])

    def test_login_w_next_url(self):
        """
        Check if login page redirects to next url if set
        """
        # create a poll for next url
        poll = self.create_test_poll()
        next_url = reverse('polls:results', args=(poll.id,))

        # relogin - this time with next url set
        post_data = dict(VALID_CREDS)
        post_data['next'] = next_url 
        response = self.client.post(LOGIN_URL, post_data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(next_url in response['Location'])
