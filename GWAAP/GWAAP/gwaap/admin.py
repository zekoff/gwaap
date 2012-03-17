'''
Created on Mar 17, 2012

@author: Zekoff
'''
from GWAAP.gwaap.models import Reference, Applicant, User, Application
from django.contrib import admin

admin.site.register(Reference)
admin.site.register(Applicant)
admin.site.register(User)
#admin.site.register(ApplicantProfile)
admin.site.register(Application)