from django.conf.urls.defaults import patterns, include, url

# Uncomment the next two lines to enable the admin:
# from django.contrib import admin
# admin.autodiscover()

urlpatterns = patterns('',
    # url(r'^$', 'GWAAP.views.home', name='home'),
    # url(r'^GWAAP/', include('GWAAP.foo.urls')),
    
    # Full path to view b/c this is technically being called from one step up the tree
    url(r'^user/$', 'gwaap.views.userActions')
)
