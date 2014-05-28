from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'test_apps.views.home', name='home'),
    # url(r'^blog/', include('blog.urls')),
    url(r'^$', 'test_apps.views.login_view', name='login_view'),
    url(r'session_security/', include('session_security.urls')),
    url(r'^blogs/', include('blogs.urls', namespace='blogs')),
    url(r'^polls/', include('polls.urls', namespace='polls')),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accounts/login/$', 'test_apps.views.login_view', name='login_view'),
    url(r'^accounts/loggedin/$', 'test_apps.views.loggedin_view', name='loggedin_view'),
    url(r'^accounts/logout/$', 'test_apps.views.logout_view', name='logout_view'),
)
