"""
Test class for polls
"""
import datetime

from django.test import TestCase
from django.utils import timezone
from polls.models import Poll, Choice
from django.core.urlresolvers import reverse
from django.contrib.auth.models import User

import test_apps.utils as utils
from django.test.utils import setup_test_environment
from django.test import Client
import unittest

from django.utils.decorators import method_decorator

setup_test_environment()

class PollMethodTests(utils.TestCaseWithUtils):
    """
    Test poll's model methods
    """
    def setUp(self):
        self.user = self.create_test_user()
        self.poll = self.create_test_poll()

    def tearDown(self):
        User.delete(self.user)
        Poll.delete(self.poll)
        
    def test_utils_create_polls(self):
        """
        Create poll to check __unicode__ for Poll and Choice
        """
        self.assertEqual(str(self.poll), 'test question')
        self.assertEqual(str(self.poll.choice_set.get(pk=1)), 'choice1')

    def test_has_voting_started_no_voting(self):
        """
        Test if voting has started without casting any votes
        """
        self.assertEqual(self.poll.has_voting_started(), False)

    def test_has_voting_started_with_voting(self, **kwargs):
        """
        Test if voting has started after casting vote
        """
        self.login()
        self.post('vote', self.poll.id, choice=1)
        self.assertEqual(self.poll.has_voting_started(), True)
        self.logout()

    def test_was_published_recently_with_future_poll(self):
        """
        Test was_published_recently with future poll
        """
        future_poll = Poll(pub_date=timezone.now() + \
                           datetime.timedelta(days=30))
        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_old_poll(self):
        """
        Test was_published_recently with old poll
        """
        future_poll = Poll(pub_date=timezone.now() - \
                           datetime.timedelta(days=30))
        self.assertEqual(future_poll.was_published_recently(), False)

    def test_was_published_recently_with_recent_poll(self):
        """
        Test was_published_recently with recent poll 
        """
        future_poll = Poll(pub_date=timezone.now() - \
                           datetime.timedelta(hours=1))
        self.assertEqual(future_poll.was_published_recently(), True)

    def test_get_eligible_voters(self):
        """
        Test list of eligible voters
        """
        self.assertTrue(all(u == p for u, p in zip(User.objects.all(), self.poll.eligible_voters())))

    def test_get_poll_winner_poll_open(self):
        """
        Test getting the poll winner when poll is open
        """
        self.assertEqual(self.poll.get_winner(), None)

    def test_get_poll_winner_poll_closed(self):
        """
        Test getting the poll winner when poll is closed
        """
        self.login()
        self.post('vote', self.poll.id, choice=1)
        self.poll.update_open_status()
        self.assertEqual(str(self.poll.get_winner()), 'choice1')
        self.logout()

    def test_reopen_poll(self):
        """
        Test reopening poll
        """
        self.login()
        self.post('vote', self.poll.id, choice=1)
        self.poll.update_open_status()
        self.assertEqual(self.poll.is_open, False)
        self.poll.reopen()
        self.assertEqual(self.poll.is_open, True)

    def test_count_votes(self):
        """
        Test vote counting
        """
        for user in utils.create_users(count=3):
            for voter in self.poll.register_voters():
                self.client.login(username=voter.user.username, password=voter.user.username)
                self.post('vote', self.poll.id, choice=1)
                self.client.logout()
        self.assertEqual(self.poll.total_votes(), 3)

class PollIndexViewTests(utils.LoginMixin, utils.TestCaseWithUtils):

    """ Test the polls index view """

    def test_index_view_with_no_polls(self):
        """
        Test index view without any polls created
        """
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls.')
        self.assertQuerysetEqual(response.context['polls']['all'], [])

    def test_index_view_with_past_poll(self):
        """
        Test index with a past poll created
        """
        question = 'test question'
        utils.create_poll(question=question, days=-30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['polls']['all'][0]['ref']), question)

    def test_index_view_with_future_poll(self):
        """
        Test index view with a future poll created
        """
        question = 'test question'
        utils.create_poll(question=question, days=30)
        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertContains(response, 'No polls.')
        self.assertQuerysetEqual(response.context['polls']['all'], [])

    def test_index_view_with_future_and_past_poll(self):
        """
        Test index view with a future and a past poll created
        """
        question1 = 'test question1'
        utils.create_poll(question=question1, days=-30)
        question2 = 'test question2'
        utils.create_poll(question=question2, days=30)

        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['polls']['all'][0]['ref']), question1)

    def test_index_view_with_two_past_polls(self):
        """
        Test index view with two past polls
        """
        question1 = 'test question1'
        utils.create_poll(question=question1, days=-30)
        question2 = 'test question2'
        utils.create_poll(question=question2, days=-40)

        response = self.client.get(reverse('polls:index'))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(str(response.context['polls']['all'][0]['ref']), question1) 
        self.assertEqual(str(response.context['polls']['all'][1]['ref']), question2)


class PollDetailViewTests(utils.LoginMixin, utils.TestCaseWithUtils):

    """ Test the polls details view """ 

    def test_detail_view_with_future_poll(self):
        """
        Test detail view with a future poll
        """
        future_poll = utils.create_poll(question='test question', days=5)
        response = self.client.get(reverse('polls:detail', args=(future_poll.id,)))
        self.assertEqual(response.status_code, 404)

    def test_detail_view_with_past_poll(self):
        """
        Test detail view with a past poll
        """
        past_poll = utils.create_poll(question='test question', days=-5)
        response = self.client.get(reverse('polls:detail', args=(past_poll.id,)))
        self.assertEqual(response.status_code, 200)

class PollVoteViewTests(utils.TestCaseWithUtils):
    """ Test the polls voting view """ 

    def setUp(self):
        self.user1 = utils.create_user(username='testuser1')
        self.user2 = utils.create_user(username='testuser2')
        self.poll = self.create_test_poll()
        self.client.login(username=self.user1.username, password=self.user1.username)

    def tearDown(self):
        self.client.logout()
        self.poll.delete()
        utils.delete_user(self.user1)
        utils.delete_user(self.user2)

    def test_vote_view_with_no_vote_selected(self):
        """
        Test vote view with a valid poll and submit it without any choice selected
        """
        response = self.client.post(reverse('polls:vote', args=(self.poll.id,)))
        self.assertContains(response, 'You did not select a choice')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.context['error_message'], 'You did not select a choice')

    def test_vote_view_with_invalid_vote_selected(self):
        """
        Test vote view with a valid poll and submit it with invalid value of choice
        """
        response = self.client.post(reverse('polls:vote', args=(self.poll.id,)), {'choice': 111 })
        self.assertContains(response, 'You did not select a choice')
        self.assertEqual(response.status_code, 200)

    def test_vote_view_with_single_user_voting(self):
        """
        Test valid poll - valid choice - single user voting
        """
        response = self.client.post(reverse('polls:vote', args=(self.poll.id,)), {'choice': 1})

        # check if redirected to right url
        self.assertEqual(response.status_code, 302)
        results_url = reverse('polls:vote_given', args=(self.poll.id,))
        self.assertTrue(results_url in response['Location'])
        self.assertEqual(self.poll.choice_set.get(pk=1).votes, 1)
        
    def test_vote_view_with_single_user_voting_follow_redirect(self):
        """
        Test vote view with a valid poll and submit it with valid value of choice - check redirected url
        """
        response = self.client.post(reverse('polls:vote', args=(self.poll.id,)), {'choice': 2}, follow=True)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(self.poll.choice_set.get(pk=2).votes, 1)
        self.assertContains(response, 'Back to main page')
        self.client.logout()


class PollResultsViewTests(utils.LoginMixin, utils.TestCaseWithUtils):

    """ Test results view """

    def test_results_view_with_invalid_poll(self):
        """
        Test results view page with invalid poll set
        """
        response = self.client.get(reverse('polls:results', args=(1,)))
        self.assertEqual(response.status_code, 404)

    def test_results_view_with_open_poll(self):
        """
        Test results view page with valid poll which is still open
        """
        poll = self.create_test_poll()
        response = self.client.get(reverse('polls:results', args=(poll.id,)))
        self.assertEqual(response.status_code, 302)

    def test_results_view_with_closed_poll(self):
        """
        Test results view page with closed poll
        """
        poll = self.create_test_poll()
        list(poll.vote_randomly())
        response = self.client.get(reverse('polls:results', args=(poll.id,)))
        self.assertEqual(response.status_code, 200)


if __name__ == '__main__':
    unittest.main()
