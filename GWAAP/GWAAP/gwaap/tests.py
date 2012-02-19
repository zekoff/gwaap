"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.

"""

from GWAAP.gwaap.models import ApplicantProfile
from django.test import TestCase
from models import Applicant, Application, User
import django.db.models
from django.db.utils import IntegrityError

#class SimpleTest(TestCase):
#    def test_basic_addition(self):
#        """
#        Tests that 1 + 1 always equals 2.
#        """
#        self.assertEqual(1 + 1, 2)

class ModelTests(TestCase):
    
    def getFreshApplicant(self, thisUsername="username"):
        applicant = Applicant(username=thisUsername)
#        applicant.save()
#        ap = ApplicantProfile(user=applicant)
#        ap.save()
#        app = Application(applicant_profile=ap)
#        app.save()
        applicant.save()
        return applicant
    
    def test_00010_userExists(self):
        user = User()
        self.assertIsInstance(user, User)
    
    def test_00020_userHasUsername(self):
        user = User()
        self.assertEqual(user.username, '')
        
    def test_00021_setUsername(self):
        user = User()
        user.username = "jimbob"
        self.assertEqual(user.username, "jimbob")
        
    def test_00030_userNameWorks(self):
        user = User()
        user.first_name = "Joe"
        user.last_name = "Tester"
        self.assertEqual(user.get_full_name(), "Joe Tester")

    def test_00040_userPassword(self):
        user = User()
        user.set_password("password42")
        self.assertTrue(user.check_password("password42"))
        
    def test_00050_applicantExists(self):
        applicant = Applicant()
        self.assertIsInstance(applicant, Applicant)
        
    def test_00060_applicationExists(self):
        app = Application()
        self.assertIsInstance(app, Application)
        
#    def test_0070_applicationHasNameField(self):
#        app = Application()
#        app.first_name = "Joe"
#        app.save()
#        self.assertEqual(app.first_name, "Joe")

#    def test_0071_applicationHasApplicantForeignKey(self):
#        app = Application()
#        applicant = Applicant()
#        applicant.save()
#        app.owner = applicant
#        app.save()
#        app = Application.objects.get(pk=1)
#        self.assertEqual(applicant, app.owner)
        
    def test_00080_applicantProfileExists(self):
        applicantProfile = ApplicantProfile()
        self.assertIsInstance(applicantProfile, ApplicantProfile)
        
    def test_00090_applicantProfileIsModel(self):
        ap = ApplicantProfile()
        self.assertIsInstance(ap, django.db.models.Model)
        
    def test_00091_applicantProfileHasId(self):
        app = Applicant(username="applicant")
        app.save()
        ap = ApplicantProfile(user=app)
        ap.save()
        apID = ap.id
        self.assertEqual(apID, 1)
        
    def test_00100_applicantHasProfile(self):
        applicant = Applicant.objects.create(username="user")
        applicant.save()
        appProfile = ApplicantProfile(user=applicant)
        appProfile.save()
        appProfile.application = Application(applicant_profile=appProfile)
        appProfile.application.save()
        self.assertIsInstance(applicant.get_profile(), ApplicantProfile)
        
    def test_00101_gettingIdOfApplicant(self):
        app = Applicant()
        app.save()
        appID = app.id
        self.assertEqual(appID, 1)
        
#    def test_0102_gettingIdOfSecondApplicant(self):
#        app = Applicant.objects.create()
#        app.save()
#        app2 = Applicant.objects.create()
#        app2.save()
#        appID = app2.id
#        self.assertEqual(appID, 2)
        
        
#This test really isn't asking anything I want to ask
#    def test_0110_applicantProfileHasApplication(self):
#        ap = ApplicantProfile()
#        self.assertIsInstance(ap.get_profile(), Application)

#    def test_0111_applicantHasProfileTwoCopies(self):
#        applicant3 = Applicant.objects.create()
#        applicant3.save()
#        applicant2 = Applicant.objects.create()
#        applicant2.save()
#        self.assertIsInstance(applicant2.get_profile(), ApplicantProfile)

    def test_00120_makeTwoApplicantsWithProfiles(self):
        applicant = Applicant(username="mr. applicant")
        applicant.save()
        ap = ApplicantProfile(user=applicant)
        ap.save()
        applicant.save()
        applicant2 = Applicant(username="mrs. applicant")
        applicant2.save()
        ap2 = ApplicantProfile(user=applicant2)
        ap2.save()
        applicant2.save()
        self.assertEqual(ap2.id, 2)
        
    def test_00130_makeSingleApplicant(self):
        applicant = Applicant(username="applicant")
        applicant.save()
        ap = ApplicantProfile(user=applicant)
        ap.save()
        applicant.save()
        self.assertIsInstance(applicant, Applicant)

    def test_00140_getApplicantById(self):
        applicant = Applicant(username="applicant")
        applicant.save()
        ap = ApplicantProfile(user=applicant)
        ap.save()
        applicant.save()
        appKey = Applicant.objects.get(username="applicant").pk
        self.assertEqual(appKey, 1)
        
    def test_00150_getApplicantByIdMultipleApplicants(self):
        applicant = Applicant(username="applicant")
        applicant.save()
        ap = ApplicantProfile(user=applicant)
        ap.save()
        applicant.save()
        applicant = Applicant(username="applicant2")
        applicant.save()
        ap = ApplicantProfile(user=applicant)
        ap.save()
        applicant.save()
        applicant = Applicant(username="applicant3")
        applicant.save()
        ap = ApplicantProfile(user=applicant)
        ap.save()
        applicant.save()
        appKey = Applicant.objects.get(username="applicant2").pk
        self.assertEqual(2, appKey)

    def test_00160_duplicateUsernamesRaisesError(self):
        applicant = Applicant(username="applicant")
        applicant.save()
        applicant = Applicant(username="applicant")
        self.assertRaises(IntegrityError, applicant.save)
        
    def test_00170_additionalProfileSaveTest(self):
        app = Applicant(username="name")
        app.save()
        app.get_profile().user = None
        ap = ApplicantProfile()
        ap.user = app
        ap.save()

    def test_00180_applicantProfileHasApplication(self):
        applicant = self.getFreshApplicant()
        application = Application.objects.get(applicant_profile=applicant.get_profile())
        self.assertIsInstance(application, Application)
        
    def testTrySignalProcessing(self):
        applicant = Applicant(username="name")
        applicant.save()
        self.assertEqual(Application.objects.get(applicant_profile=applicant.get_profile()).intTest, 1)
        
