from django.conf.urls import patterns, include, url

from django.contrib import admin
admin.autodiscover()

urlpatterns = patterns('',
    # Examples:
    url(r'^$', 'app.views.home', name='home'),
	url(r'^feeds/(.*)$', 'app.views.feeds'),
	url(r'^mom/(.*)$', 'app.views.mom'),
	url(r'^cmom/(.*)$', 'app.views.cmom'),
	url(r'^tasks/(.*)$', 'app.views.tasks'),
	url(r'^ctasks/(.*)$', 'app.views.ctasks'),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^accept/(.*)$', 'app.views.accept_task'),
    url(r'^submit/(.*)$', 'app.views.submit_task'),
    url(r'^alltasks/(.*)$', 'app.views.alltask'),
    url(r'^mytasks/(.*)$', 'app.views.mytask'),
    url(r'generatefile/(.*)$', 'app.views.generate_file'),
    url(r'logout/$', 'app.views.logout'),
)
