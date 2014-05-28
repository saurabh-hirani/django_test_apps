from django.conf.urls import patterns,url
from blogs import views

urlpatterns = patterns('',
    url(r'^$', views.index, name='index'),
)
