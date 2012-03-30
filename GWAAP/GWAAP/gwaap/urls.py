from django.conf.urls.defaults import patterns, url
from GWAAP import settings

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
    url(r'^view_application/$', 'viewApplication'),
    url(r'^view_profile/$', 'viewProfile'),
    url(r'^upload_resume/$', 'uploadResume'),
    url(r'^upload_letter/$', 'uploadLetter'),
    # User URLs
    url(r'^user/$', 'userActions'),
    url(r'^user/login/$', 'userLogin'),
    url(r'^user/display_applicants/$', 'displayApplicants'),
    url(r'^user/view_applicant/(?P<applicant_pk>.*)/$', 'viewApplicant'),
    url(r'^user/make_comment/(?P<applicant_pk>.*)/$', 'makeComment'),
    url(r'^user/cast_vote/(?P<applicant_pk>.*)/$', 'castVote'),
    url(r'^user/search_applicants/', 'searchApplicants'),
    
    #TEMP
    url(r'^test/$', 'testView'),
)

if settings.DEBUG:
    urlpatterns += patterns('',
        url(r'^(?P<path>.*)$', 'django.views.static.serve', {
            'document_root': settings.MEDIA_ROOT,
        }),
   )
