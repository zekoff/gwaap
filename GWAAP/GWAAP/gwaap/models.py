from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save

# Create your models here.
class User(User):
    pass

class Applicant(User):
    pass

class Application(models.Model):
    pass

class ApplicantProfile(models.Model):
    user = models.OneToOneField(Applicant)
#    application = models.OneToOneField(Application)

def create_user_profile(sender, instance, created, **kwargs):
    if created:
        # Was using ApplicantProfile.objects.get(user=instance)
        # This wasn't working, so changed to get_or_create from a StackOverflow answer
        # http://stackoverflow.com/questions/6388105/django-integrityerror-column-user-id-is-not-unique
        ApplicantProfile.objects.get_or_create(user=instance)
        
post_save.connect(create_user_profile, sender=Applicant)
