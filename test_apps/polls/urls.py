from django.conf.urls import patterns,url
from polls import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
    url(r'^(?P<poll_id>\d+)/$', views.detail, name='detail'),
    url(r'^(?P<poll_id>\d+)/results/$', views.results, name='results'),
    url(r'^(?P<poll_id>\d+)/vote/$', views.vote, name='vote'),
    url(r'^(?P<poll_id>\d+)/vote_given/$', views.vote_given, name='vote_given'),
    url(r'^reopen/$', views.reopen, name='reopen'),
    url(r'^vote_randomly/$', views.vote_randomly, name='vote_randomly'),
)
