from django.contrib.auth.models import Permission
from django.db import models
from django.db.models.signals import post_save
from django.dispatch.dispatcher import receiver
from django.contrib.auth.models import User as DjangoUser
import string
import random

# Create your models here.
class User(DjangoUser):
    class Meta:
        permissions = (
            ('is_gwaap_user', 'Is a faculty/admin user of the GWAAP system.'),
        )
    def __unicode__(self):
        return self.username

class Applicant(DjangoUser):
    class Meta:
        permissions = (
            ('is_gwaap_applicant', 'Is an applicant using the GWAAP system for applicant tracking.'),
        )
    def get_application(self):
        return Application.objects.get(applicant_profile=self.get_profile())
    def __unicode__(self):
        return self.username
    
class Application(models.Model):
    applicant_profile = models.ForeignKey('ApplicantProfile', unique=True)
    def __unicode__(self):
        return 'Application belonging to ' + str(self.applicant_profile.user.username)

class Reference(models.Model):
    attached_to = models.ForeignKey(Application)
    email = models.EmailField()
    unique_id = models.CharField(max_length=12, unique=True)
    comments = models.TextField()
    name = models.CharField(max_length=60)
    affiliation = models.CharField(max_length=60)
    def __unicode__(self):
        return 'Referral by ' + str(self.name) + ' on behalf of ' + str(self.attached_to.applicant_profile.user.username)

class ApplicantProfile(models.Model):
    user = models.ForeignKey(DjangoUser, unique=True)
    def __unicode__(self):
        return "Django profile info for " + str(self.user.username)
    
class Comment(models.Model):
    class Meta:
        permissions = (
            ('can_comment', 'Can make comments on applications.'),
        )
    attached_to = models.ForeignKey(Application)
    made_by = models.ForeignKey(User, blank=True, null=True)
    content = models.TextField()
    def __unicode__(self):
        return "Comment on the application of " + str(self.attached_to.applicant_profile.username)
    
class Vote(models.Model):
    class Meta:
        permissions = (
            ('can_vote', 'Can cast votes on applications.'),
        )
    VOTE_CHOICES = (
                    (1, 'Strong Reject'),
                    (2, 'Weak Reject'),
                    (3, 'Weak Accept'),
                    (4, 'Strong Accept')
                )
    attached_to = models.ForeignKey(Application)
    made_by = models.ForeignKey(User, blank=True, null=True)
    content = models.PositiveSmallIntegerField(null=True, choices=VOTE_CHOICES)
    def __unicode__(self):
        return Vote.VOTE_CHOICES[self.content - 1][1] + " for " + str(self.attached_to.applicant_profile.user.username)
    
@receiver(post_save, sender=Applicant, dispatch_uid="multiple_dispatch_bugfix")
def create_applicant(sender, instance, created, **kwargs):
    if created:
        applicantprofile = ApplicantProfile.objects.create(user=instance)
        Application.objects.create(applicant_profile=applicantprofile)
        applicant_permission = Permission.objects.get(codename="is_gwaap_applicant")
        instance.user_permissions.add(applicant_permission)
        
@receiver(post_save, sender=User, dispatch_uid="give_users_identification")
def create_user(sender, instance, created, **kwargs):
    if created:
        permission = Permission.objects.get(codename="is_gwaap_user")
        instance.user_permissions.add(permission)
        
@receiver(post_save, sender=Reference, dispatch_uid="reference_unique_id")
def create_reference(sender, instance, created, **kwargs):
    if created:
        matches = [1, 2]
        random_string = ''
        while len(matches) > 0:
            random_string = id_generator()
            matches = Reference.objects.filter(unique_id=random_string)
        instance.unique_id = random_string
        instance.save()

# Random string generator, based on http://stackoverflow.com/questions/2257441/python-random-string-generation-with-upper-case-letters-and-digits
def id_generator(size=6, chars=string.ascii_uppercase + string.digits + string.lowercase):
    return ''.join(random.choice(chars) for x in range(size)) #@UnusedVariable
