from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('gwaap.views',
    # Full path to view b/c this is technically being called from one step up the tree
    # Applicant URLs
    url(r'^$', 'applicantHome'),
    url(r'^login/$', 'applicantLogin'),
    url(r'^add_reference/$', 'applicantAddReference'),
    url(r'^reference/(?P<unique_id>.*)/$', 'completeReference'),
    # User URLs
    url(r'^user/$', 'userActions'),
    url(r'^user/login/$', 'userLogin')
)
