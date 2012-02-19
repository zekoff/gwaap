from django.contrib.auth.models import User
from django.db import models
from django.db.models.signals import pre_save, post_save
from django.dispatch.dispatcher import receiver
#from django.db.models.signals import post_save, pre_save

# Create your models here.
class User(User):
    pass

class Applicant(User):
    pass

class Application(models.Model):
    # It's in quotes b/c the ApplicantProfile class hasn't been defined yet at this point in parsing
    applicant_profile = models.ForeignKey('ApplicantProfile', unique=True)
    intTest = models.IntegerField(default=1)

class ApplicantProfile(models.Model):
    user = models.ForeignKey(Applicant, unique=True)
#    application = models.ForeignKey(Application, unique=True)
    
@receiver(post_save, sender=Applicant, dispatch_uid="multiple_dispatch_fix")
def create_applicant(sender, instance, created, **kwargs):
    if created:
        applicantprofile = ApplicantProfile.objects.create(user=instance)
        application = Application.objects.create(applicant_profile=applicantprofile)
        
#@receiver(post_save, sender=ApplicantProfile)
#def create_application(sender, instance, created, **kwargs):
#    if created:
#        (application, created) = Application.objects.get_or_create()
    
#def create_user_profile(sender, instance, created, **kwargs):
#    if created:
#        pass
#        # Was using ApplicantProfile.objects.get(user=instance)
#        # This wasn't working, so changed to get_or_create from a StackOverflow answer
#        # http://stackoverflow.com/questions/6388105/django-integrityerror-column-user-id-is-not-unique
##        ApplicantProfile.objects.get_or_create(user=instance)
#        ApplicantProfile.objects.create(user=instance)
##        ap = ApplicantProfile(user=instance)
##        ap.save()
#        
#post_save.connect(create_user_profile, sender=Applicant)
## See http://www.turnkeylinux.org/blog/django-profile for another method of doing this
