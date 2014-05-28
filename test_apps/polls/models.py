""" Models for the poll app """
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User

import datetime
import random

# Create your models here.

class Poll(models.Model):
    """ Poll model """
    question = models.CharField(max_length=200, unique=True)
    pub_date = models.DateTimeField('date published')
    is_open = models.BooleanField(default=True)

    def has_voting_started(self):
        return any(choice.votes > 0 for choice in self.choice_set.all())

    def __unicode__(self):
        """ represent object """
        return self.question

    def was_published_recently(self):
        """ was this poll added recently """
        now = timezone.now()
        return now - datetime.timedelta(days=1) <= self.pub_date < now

    was_published_recently.boolean = True
    # represents pub_date so when you sort on it - sort on pub_date
    # if not set - it will not be sortable in the UI
    was_published_recently.admin_order_field = 'pub_date'
    was_published_recently.short_description = 'Published recently?'

    def eligible_voters(self):
        return User.objects.all()

    def get_winner(self):
        if self.is_open: 
            return None
        return max(self.choice_set.all(), key = lambda c: c.votes)

    def update_open_status(self):
        """
        Check if poll ought to be closed - if all voters have voted
        """
        n_voted = [v for v in self.voter_set.all() if v.has_voted == True]
        if len(self.eligible_voters()) == len(n_voted):
            self.is_open = False
            self.save()
        return self.is_open

    def reopen(self):
        """
        Reopen poll
        """
        # set vote count to 0 for all choices
        choices = self.choice_set.all()
        for choice in choices:
            choice.votes = 0
            choice.save()

        # set has_voted flag for all voters
        voters = self.voter_set.all()
        for voter in voters:
            voter.has_voted = False
            voter.save()

        self.is_open = True
        self.save()
        return True

    def total_votes(self):
        """
        Count total votes for this poll
        """
        total = 0
        choices = self.choice_set.all()
        for choice in choices:
            total += choice.votes
        return total            

    def vote_randomly(self):
        """
        Perform random voting on this poll
        """
        not_voted = list(self.voter_set.filter(has_voted=False))
        choices = self.choice_set.all()
        random.shuffle(not_voted)
        for voter in not_voted:
            rand_choice = random.choice(choices)
            rand_choice.votes += 1
            voter.has_voted = True
            rand_choice.save()
            voter.save()
            yield (voter, rand_choice)
        self.update_open_status()

    def register_voters(self):
        """
        Register voters for this poll
        """
        # voter count should be equal to total user count
        eligible_voters = self.eligible_voters()
        if len(eligible_voters) != self.voter_set.count:
            usernames = set([u.username for u in eligible_voters])
            voters = set([v.user.username for v in self.voter_set.all()])
            not_added = usernames - voters
            # add the difference of users to the voter list
            if not_added:
                not_added = list(not_added)
                not_added.sort()
                for username in not_added:
                    user = User.objects.get(username=username)
                    voter = Voter(poll=self, user=user, has_voted=False)
                    voter.save()
                    yield voter

    def save(self, *args, **kwargs):
        """
        Save the Poll model - register users to Voter list upon form save
        """
        super(Poll, self).save(*args, **kwargs)
        if len(self.voter_set.all()) == 0:
            list(self.register_voters())
        
class Choice(models.Model):
    """ Choice model """
    poll = models.ForeignKey(Poll)
    choice_text = models.CharField(max_length=200)
    votes = models.IntegerField(default=0)

    def __unicode__(self):
        """ represent object """
        return self.choice_text

class Voter(models.Model):
    """
    Model to check which users have voted
    """
    class Meta:
        unique_together = ['poll', 'user']

    poll = models.ForeignKey(Poll)
    user = models.ForeignKey(User)
    has_voted = models.BooleanField(default=False)

    def __unicode__(self):
        """ represent object """
        return self.user.username
