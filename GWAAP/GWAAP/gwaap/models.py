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
    def get_gwaap_profile(self):
        return GwaapProfile.objects.get(applicant_profile=self.get_profile())
    def __unicode__(self):
        return self.username
    

def applicant_upload_filename(instance, filename):
    return "applicant_files/" + str(instance.applicant_profile.user.username) + "/" + filename

STATUS_CODE = (
    (0, "Complete"),
    (1, "Incomplete"),
    (2, "Pending"),
    (3, "Partial"),
    (4, "Not Received"),
    (5, "Not Applicable"),
    (6, "Contact Administrator")
)

APPLICATION_STATUS = (
    (0, "Collecting information"),
    (1, "Undergoing initial review by GPO"),
    (2, "Undergoing review by admissions committee"),
    (3, "Undergoing decision by department"),
    (4, "Forwarded to Graduate School for final decision"),
    (5, "Complete")
)

class Application(models.Model):
    applicant_profile = models.ForeignKey('ApplicantProfile', unique=True)
    status = models.SmallIntegerField(default=0, choices=APPLICATION_STATUS)
    resume = models.FileField(upload_to=applicant_upload_filename, blank=True)
    letter_of_intent = models.FileField(upload_to=applicant_upload_filename, blank=True)
    transcript_status = models.SmallIntegerField(default=5, choices=STATUS_CODE)
    gre_status = models.SmallIntegerField(default=5, choices=STATUS_CODE)
    toefl_status = models.SmallIntegerField(default=5, choices=STATUS_CODE)
    def __unicode__(self):
        return 'Application belonging to ' + str(self.applicant_profile.user.username)

RELATIVE_RANK = (
    (0, "Upper 1%"),
    (1, "Upper 10%"),
    (2, "Upper 25%"),
    (3, "Upper 50%"),
    (4, "Lower 50%"),
    (5, "Not observed")
)

OVERALL_RECOMMENDATION = (
    (0, "Do not recommend"),
    (1, "Recommend with reservations"),
    (2, "Recommend"),
    (3, "Strongly recommend")
)

class Reference(models.Model):
    attached_to = models.ForeignKey(Application)
    email = models.EmailField()
    unique_id = models.CharField(max_length=12, unique=True)
    comments = models.TextField(blank=True)
    name = models.CharField(max_length=90, default="unknown", blank=True)
    affiliation = models.CharField(max_length=90, blank=True)
    complete = models.BooleanField(default=False)
    integrity = models.SmallIntegerField(default=5, choices=RELATIVE_RANK)
    development = models.SmallIntegerField(default=5, choices=RELATIVE_RANK)
    communication = models.SmallIntegerField(default=5, choices=RELATIVE_RANK)
    motivation = models.SmallIntegerField(default=5, choices=RELATIVE_RANK)
    research = models.SmallIntegerField(default=5, choices=RELATIVE_RANK)
    overall = models.SmallIntegerField(default=0, choices=OVERALL_RECOMMENDATION)
    def __unicode__(self):
        return 'Referral by ' + str(self.name) + ' on behalf of ' + str(self.attached_to.applicant_profile.user.username)

class GwaapProfile(models.Model):
    '''
    This is the semantic representation of an applicant's profile information. It includes all fields
    referred to in the GWAAP dump that aren't already covered by the Django User model (i.e. everything
    except for first name, last name, and email).
    There are localization and default options available through Django for some of these fields
    (for instance, state) but they are represented here as pure character fields to accommodate
    international students and blank fields where necessary. It appears that some could be boolean fields
    or number fields as well, but they are implemented as CharFields here for similar reasons.
    '''
    applicant_profile = models.ForeignKey('ApplicantProfile', unique=True)
    # First name in Django User model
    # Last name in Django User model
    middle_name = models.CharField(max_length=90, blank=True)
    street1 = models.CharField(max_length=90, blank=True)
    street2 = models.CharField(max_length=90, blank=True)
    city = models.CharField(max_length=90, blank=True)
    province = models.CharField(max_length=90, blank=True)
    state = models.CharField(max_length=90, blank=True)
    country = models.CharField(max_length=90, blank=True)
    zip_code = models.CharField(max_length=30, blank=True)
    # Email in Django User model
    phone = models.CharField(max_length=30, blank=True)
    birthday = models.CharField(max_length=30, blank=True)
    gender = models.CharField(max_length=30, blank=True)
    country_birth = models.CharField(max_length=90, blank=True)
    citizenship = models.CharField(max_length=90, blank=True)
    ref_number = models.CharField(max_length=90, blank=True)
    date_apply = models.CharField(max_length=30, blank=True)
    enter_qtr = models.CharField(max_length=30, blank=True)
    enter_year = models.CharField(max_length=30, blank=True)
    degree = models.CharField(max_length=90, blank=True)
    major = models.CharField(max_length=90, blank=True)
    gre_taken = models.CharField(max_length=30, blank=True)
    o_gre_v = models.CharField(max_length=30, blank=True)
    o_gre_q = models.CharField(max_length=30, blank=True)
    o_gre_a = models.CharField(max_length=30, blank=True)
    o_gre_w = models.CharField(max_length=30, blank=True)
    toefl_taken = models.CharField(max_length=30, blank=True)
    o_toefl_score = models.CharField(max_length=30, blank=True)

class ApplicantProfile(models.Model):
    '''
    This is a Django-centric model whose only job is to link an Applicant with their Application
    and GWAAP profile object. Those two objects hold references to this one as foreign keys. This
    model has no semantic raison d'etre; it falls out of the Django User weirdness. It is referred
    to in the settings.py file.
    '''
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
        return "Comment on the application of " + str(self.attached_to.applicant_profile.user.username)
    
VOTE_CHOICES = (
    (0, 'Strong Reject'),
    (1, 'Weak Reject'),
    (2, 'Weak Accept'),
    (3, 'Strong Accept')
)

class Vote(models.Model):
    class Meta:
        permissions = (
            ('can_vote', 'Can cast votes on applications.'),
        )
    attached_to = models.ForeignKey(Application)
    made_by = models.ForeignKey(User, blank=True, null=True)
    content = models.PositiveSmallIntegerField(null=True, choices=VOTE_CHOICES)
    def __unicode__(self):
        return VOTE_CHOICES[self.content][1] + " by " + str(self.made_by) + " for " + str(self.attached_to.applicant_profile.user.username)
    
@receiver(post_save, sender=Applicant, dispatch_uid="multiple_dispatch_bugfix")
def create_applicant(sender, instance, created, **kwargs):
    if created:
        applicantprofile = ApplicantProfile.objects.create(user=instance)
        Application.objects.create(applicant_profile=applicantprofile)
        GwaapProfile.objects.create(applicant_profile=applicantprofile)
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
def id_generator(size=10, chars=string.ascii_uppercase + string.digits + string.lowercase):
    return ''.join(random.choice(chars) for x in range(size)) #@UnusedVariable
