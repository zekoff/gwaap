from django.conf.urls.defaults import patterns, include, url
#from django.contrib import admin

# Uncomment the next two lines to enable the admin:
from django.contrib import admin
#admin.autodiscover()
from GWAAP.gwaap import admin as gwaap_admin #@UnusedImport

urlpatterns = patterns('',
    # Examples:
    # url(r'^$', 'GWAAP.views.home', name='home'),
    # url(r'^GWAAP/', include('GWAAP.foo.urls')),

    # Uncomment the admin/doc line below to enable admin documentation:
    # url(r'^admin/doc/', include('django.contrib.admindocs.urls')),

    # Uncomment the next line to enable the admin:
    url(r'^admin/', include(admin.site.urls)),
#    url(r'^$', 'gwaap.views.pagetest'),
    url(r'', include('gwaap.urls'))
)
