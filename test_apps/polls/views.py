"""
Poll views file
"""

from django.shortcuts import render
from django.http import HttpResponseRedirect
from django.core.urlresolvers import reverse
from django.utils import timezone
from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User

from polls.models import Poll, Choice
from test_apps.utils import anonymous_required, required_poll_status, required_voting_status
from test_apps.utils import render_template

# Create your views here.

def get_preview_context():
    return {
        'app_objects': Poll.objects.all(),
    }

@login_required
def index(request):
    """
    Index page
    """
    polls = Poll.objects.filter(pub_date__lte=timezone.now())
    open_polls = [p for p in polls if p.is_open is True]
    closed_polls = list(set(polls) - set(open_polls))
    user_open_polls = [p for p in open_polls for v in \
                       p.voter_set.filter(user=request.user) if v.has_voted is False]

    context = {
        'polls': {
            'all': [],
            'open': [],
            'closed': [],
            'user_open': [],
        },
    }

    for poll in polls:
        poll_data = {}
        poll_data['ref'] = poll
        poll_data['status'] = 'closed'
        if poll in open_polls:
            if poll in user_open_polls:
                poll_data['status'] = 'user_open'
            else:
                poll_data['status'] = 'open'
        context['polls']['all'].append(poll_data)

    for poll in open_polls:
        poll_data = {}
        n_eligible_voters = len(poll.eligible_voters())
        poll_data['ref'] = poll
        poll_data['poll_voters'] = [v for v in poll.voter_set.all() if v.has_voted is True]
        poll_data['pending_voters'] = [v for v in poll.voter_set.all() if v.has_voted is False]
        context['polls']['open'].append(poll_data)

    for poll in closed_polls:
        poll_data = {}
        poll_data['ref'] = poll
        poll_data['winner'] = poll.get_winner()
        context['polls']['closed'].append(poll_data)

    for poll in user_open_polls:
        poll_data = {}
        poll_data['ref'] = poll
        context['polls']['user_open'].append(poll_data)

    return render_template(request, 'polls/index.html', context)

@required_poll_status(True)
@required_voting_status(False)
@login_required
def detail(request, poll_id, **kwargs):
    """
    Detail page
    """
    poll = kwargs['poll']
    return render_template(request, 'polls/detail.html', {'poll': poll })

@required_poll_status(True)
@required_voting_status(False)
@login_required
def vote(request, poll_id, **kwargs):
    """
    Vote form handler
    """
    poll = kwargs['poll']
    try:
        selected_choice = poll.choice_set.get(pk=request.POST['choice'])
    except (KeyError, Choice.DoesNotExist):
        return render(request, 'polls/detail.html', {
            'poll': poll,
            'error_message': "You did not select a choice"
        })
    else:
        # increment vote count
        selected_choice.votes += 1
        selected_choice.save()

        # set has_voted True for this user for this poll
        voter = kwargs['voter']
        voter.has_voted = True
        voter.save()
        
        # check how many pending voters left
        poll.update_open_status()
        if poll.is_open:
            return HttpResponseRedirect(reverse('polls:vote_given', args=(poll.id,)))
        return HttpResponseRedirect(reverse('polls:results', args=(poll.id,)))

@required_poll_status(True)
@required_voting_status(True)
@login_required
def vote_given(request, poll_id, **kwargs):
    """
    Voting done handler
    """
    poll = kwargs['poll']
    # get pending voters
    all_voters = poll.voter_set.all()
    pending_voters = poll.voter_set.filter(has_voted=False)

    context = {
        'poll': poll,
        'all_voters': all_voters,
        'pending_voters': pending_voters
    }
    return render_template(request, 'polls/vote_given.html', context)

@required_poll_status(False)
@required_voting_status(True)
@login_required
def results(request, poll_id, **kwargs):
    """
    Results page
    """
    poll = kwargs['poll']
    ranked_choices = poll.choice_set.order_by('-votes')
    return render_template(request, 'polls/results.html', {'poll': poll, 'ranked_choices': ranked_choices })

#@required_poll_status(False)
#@required_voting_status(True)
@login_required
def reopen(request, **kwargs):
    """
    Reopen selected polls
    """
    for poll_id in request.POST.getlist('poll_ids'):
        poll = Poll.objects.get(pk=poll_id)
        print poll
        poll.reopen()
    return HttpResponseRedirect(reverse('polls:index') + '#open_polls_tab')

@login_required
def vote_randomly(request, **kwargs):
    """
    Randomly vote in the selected polls
    """
    for poll_id in request.POST.getlist('poll_ids'):
        poll = Poll.objects.get(pk=poll_id)
        list(poll.vote_randomly())
    return HttpResponseRedirect(reverse('polls:index') + '#closed_polls_tab')
