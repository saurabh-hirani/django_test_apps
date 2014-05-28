# coding: utf-8
from django.test.client import Client
from django.core.urlresolvers import reverse
from polls.models import  Poll, Choice, Voter
c = Client()
p = Poll.objects.all()[0]
