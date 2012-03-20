from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('gwaap.views',
    # Full path to view b/c this is technically being called from one step up the tree
    url(r'^logout/$', 'logoutView'),
    # Applicant URLs
    url(r'^$', 'applicantHome'),
    url(r'^login/$', 'applicantLogin'),
    url(r'^add_reference/$', 'applicantAddReference'),
    url(r'^reference/(?P<unique_id>.*)/$', 'completeReference'),
    # User URLs
    url(r'^user/$', 'userActions'),
    url(r'^user/login/$', 'userLogin'),
    url(r'^user/display_applicants/$', 'displayApplicants'),
    url(r'^user/view_applicant/(?P<applicant_pk>.*)/$', 'viewApplicant'),
    url(r'^user/make_comment/(?P<applicant_pk>.*)/$', 'makeComment'),
    url(r'^user/cast_vote/(?P<applicant_pk>.*)/$', 'castVote'),
    
    #TEMP
    url(r'^test/$', 'testView'),
)
