"""
Customized admin interface for Poll
"""
from django.contrib import admin
from polls.models import Poll
from polls.models import Choice
from polls.models import Voter
from django.contrib.auth.models import User

class ChoiceInline(admin.TabularInline):
    """
    Inline choice class
    """
    model = Choice
    extra = 3

class VoterInline(admin.TabularInline):
    """
    Inline choice class
    """
    model = Voter

class PollAdmin(admin.ModelAdmin):
    """
    Admin view poll class
    """
    fieldsets = [
        (None, {'fields': ['question']}),
        ('Date information', {'fields': ['pub_date']}),
        ('Active', {'fields': ['is_open']}),
    ]
    inlines = [ChoiceInline, VoterInline]
    list_display = ('question', 'pub_date', 'is_open', 'was_published_recently')
    list_filter = ['pub_date']
    search_fields = ['question']
    #fields = ['pub_date', 'question']

    #def save_model(self, request, obj, form, change):
    #    """
    #    Save the Poll model - register users to Voter list upon form save
    #    """
    #    obj.save()
    #    if User.objects.count != obj.voter_set.count:
    #        usernames = set([u.username for u in User.objects.all()])
    #        voters = set([v.user.username for v in obj.voter_set.all()])
    #        not_added = usernames - voters
    #        if not_added:
    #            for username in not_added:
    #                user = User.objects.get(username=username)
    #                voter = Voter(poll=obj, user=user, has_voted=False)
    #                voter.save()

# Register your models here.
admin.site.register(Poll, PollAdmin)
#admin.site.register(Choice)
