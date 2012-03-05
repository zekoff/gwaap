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
from django.test.client import Client, RequestFactory
from GWAAP.gwaap.views import userActions
from django.contrib.auth.models import Permission

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
        apID = app.get_profile().id
        self.assertEqual(apID, 1)
        
    def test_00100_applicantHasProfile(self):
        applicant = Applicant.objects.create(username="user")
        applicant.save()
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
        applicant2 = Applicant(username="mrs. applicant")
        applicant2.save()
        self.assertEqual(applicant2.id, 2)
        
    def test_00130_makeSingleApplicant(self):
        applicant = Applicant(username="applicant")
        applicant.save()
        self.assertIsInstance(applicant, Applicant)

    def test_00140_getApplicantById(self):
        applicant = Applicant(username="applicant")
        applicant.save()
        appKey = Applicant.objects.get(username="applicant").pk
        self.assertEqual(appKey, 1)
        
    def test_00150_getApplicantByIdMultipleApplicants(self):
        applicant = Applicant(username="applicant")
        applicant.save()
        applicant = Applicant(username="applicant2")
        applicant.save()
        applicant = Applicant(username="applicant3")
        applicant.save()
        appKey = Applicant.objects.get(username="applicant2").pk
        self.assertEqual(2, appKey)

    def test_00160_duplicateUsernamesRaisesError(self):
        applicant = Applicant(username="applicant")
        applicant.save()
        applicant = Applicant(username="applicant")
        self.assertRaises(IntegrityError, applicant.save)
        
    def test_00170_deleteProfileAndCreateNewOne(self):
        app = Applicant(username="name")
        app.save()
        ApplicantProfile.objects.get(user=app).delete()
        ap = ApplicantProfile()
        ap.user = app
        ap.save()

    def test_00180_applicantProfileHasApplication(self):
        applicant = self.getFreshApplicant()
        application = Application.objects.get(applicant_profile=applicant.get_profile())
        self.assertIsInstance(application, Application)
        
#    def test_00190_trySignalProcessing(self):
#        applicant = Applicant(username="name")
#        applicant.save()
#        self.assertEqual(Application.objects.get(applicant_profile=applicant.get_profile()).intTest, 1)
        
    def test_00200_getApplicationConvenienceMethod(self):
        applicant = Applicant(username="user")
        applicant.save()
        self.assertIsInstance(applicant.get_application(), Application)

class ViewTests(TestCase):
    
    def getRequest(self, address):
        # This allows tests to skip the url.py file while testing
        # BUT does not allow for sessions
        return RequestFactory().get(address)
    
#    def test_00010_userActionsViewExists(self):
#        client = Client()
#        response = client.get('/user/')
#        self.assertEqual(response.status_code, 200)
        
    def test_00020_userActionsIsCorrectPage(self):
        client = Client()
        user = User.objects.create(username='alan')
        user.set_password('password')
        user.save()
        client.login(username='alan', password='password')
        response = client.get('/user/')
        self.assertEqual(response.content, 'User Actions')
        
#    def test_00021_applicantCannotLoginToUserArea(self):
#        client = Client()
#        applicant = Applicant.objects.create(username='app')
#        applicant.set_password('pass')
#        applicant.save()
#        client.login(username='app', password='pass')
#        response = client.get('/user/')
#        self.assertEqual(response.status_code, 302)
        
#    def test_00030_djangoResponseFactoryTest(self):
#        response = userActions(self.getRequest('/user/'))
#        self.assertEqual(response.status_code, 200)
        
    def test_00040_unauthenticatedUserGetsRedirected(self):
        client = Client()
        response = client.get('/user/')
        self.assertEqual(response.status_code, 302)
        
#    def test_00050_userLoginPresentsForm(self):
#        client = Client()

    def test_00050_isUserPermissionExists(self):
        permission = Permission.objects.get(codename='is_gwaap_user')
        self.assertIsInstance(permission, Permission)
        
    def test_00060_usersAutomaticallyGetUserPermission(self):
        user = User.objects.create(username="newuser")
        user.set_password("pass")
        user.save()
        self.assertTrue(user.has_perm('gwaap.is_gwaap_user'))
        
    def test_00070_applicantsDontHaveUserPermission(self):
        applicant = Applicant.objects.create(username="applicantman")
        applicant.set_password("pass")
        applicant.save()
        self.assertFalse(applicant.has_perm('gwaap.is_gwaap_user'))
        
    def test_00080_usersCanViewActionsPage(self):
        client = Client()
        user = User.objects.create(username="userman")
        user.set_password("passs")
        user.save()
        client.login(username="userman", password="passs")
        response = client.get('/user/')
        self.assertEqual(response.content, 'User Actions')
        
    def test_00090_applicantsGetRedirected(self):
        client = Client()
        app = Applicant.objects.create(username="applicant")
        app.set_password("pass")
        app.save()
        client.login(username="applicant", password="pass")
        response = client.get('/user/')
        self.assertEqual(response.status_code, 302)
        
    def test_00100_unauthenticatedUserGoesToLogin(self):
        client = Client()
        response = client.get('/user/')
        self.assertRedirects(response, '/user/login/?next=/user/')
        
    def test_00110_userLoginFormIsRealForm(self):
        client = Client()
        response = client.get('/user/login/')
        self.assertContains(response, "<form")
        
    def test_00120_userLoginFormAcceptsPostDataAndFails(self):
        client = Client()
        data = dict(username='testuser', password='password')
        response = client.post('/user/login/', data)
        self.assertContains(response, "Authentication failed")
        
    def test_00130_userLoginAcceptsGoodLoginData(self):
        client = Client()
        data = dict(username='testuser', password='password')
        user = User.objects.create(username='testuser')
        user.set_password('password')
        user.save()
        response = client.post('/user/login/', data)
        self.assertContains(response, 'Logged in')
        
    def test_00140_applicantFailsUserLogin(self):
        client = Client()
        data = dict(username='applicant', password='pass')
        app = Applicant.objects.create(username='applicant')
        app.set_password('pass')
        app.save()
        response = client.post('/user/login/', data)
        self.assertContains(response, 'Authentication failed')
        
    def test_00150_applicantHomePageExists(self):
        client = Client()
        response = client.get('/')
        self.assertTrue(response.status_code in [200, 302])
#        self.assertContains(response, 'Applicant Home')
        
    def test_00160_applicantHomePageRequiresLogin(self):
        client = Client()
        app = Applicant.objects.create(username='applicant')
        app.set_password('pass')
        app.save()
        # do NOT login user
        response = client.get('/', follow=True)
        self.assertContains(response, 'Applicant Login')
        
    def test_00170_applicantLoginPageExists(self):
        client = Client()
        response = client.get('/login/')
        self.assertContains(response, 'Applicant Login')
        
    def test_00180_applicantHomeRequiresApplicantPermission(self):
        client = Client()
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client.login(username='user', password='pass')
        response = client.get('/', follow=True)
        self.assertContains(response, 'Applicant Login')
        
    def test_00190_applicantsHaveApplicantPermission(self):
        client = Client()
        app = Applicant.objects.create(username='applicant')
        app.set_password('password')
        app.save()
        client.login(username='applicant', password='password')
        response = client.get('/')
        self.assertContains(response, 'Applicant Home')

    def test_00200_applicantPermissionExists(self):
        perm = Permission.objects.get(codename="is_gwaap_applicant")
        self.assertIsInstance(perm, Permission)
      
    def test_00210_applicantAutomaticallyGetsApplicantPermission(self):
        applicant = Applicant.objects.create(username="applicant")
        self.assertTrue(applicant.has_perm('gwaap.is_gwaap_applicant'))
        
    def test_00220_applicantLoginHasForm(self):
        client = Client()
        app = Applicant.objects.create(username='applicant')
        app.set_password('password')
        app.save()
        client.login(username='applicant', password='password')
        response = client.get('/login/')
        self.assertContains(response, '<form')
        
    def test_00230_applicantLoginAcceptsPost(self):
        client = Client()
        app = Applicant.objects.create(username='applicant')
        app.set_password('password')
        app.save()
        data = dict(username='applicant', password='password')
        response = client.post('/login/', data)
        self.assertContains(response, 'Logged in')
        
    def test_00240_applicantLoginRejectsUsers(self):
        client = Client()
        user = User.objects.create(username="baduser")
        user.set_password("pass")
        user.save()
        data = dict(username='baduser', password='pass')
        response = client.post('/login/', data)
        self.assertContains(response, 'Authentication failed')
