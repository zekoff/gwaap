from GWAAP.gwaap.models import ApplicantProfile, Reference, Comment, Vote, \
    STATUS_CODE, RELATIVE_RANK, VOTE_CHOICES, GwaapProfile
from django.contrib.auth.models import Permission
from django.core import mail
from django.core.mail import send_mail
from django.db.models.fields.files import FieldFile
from django.db.utils import IntegrityError
from django.test import TestCase
from django.test.client import Client, RequestFactory
from models import Applicant, Application, User
import django.db.models
from django.core.files.base import File #@UnusedImport
from django.core.files.uploadedfile import UploadedFile #@UnusedImport


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
        self.assertContains(response, 'User Actions')
        
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
        self.assertContains(response, 'User Actions')
        
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
        response = client.post('/user/login/', data, follow=True)
        self.assertContains(response, "Authentication failed")
        
    def test_00130_userLoginAcceptsGoodLoginData(self):
        client = Client()
        data = dict(username='testuser', password='password')
        user = User.objects.create(username='testuser')
        user.set_password('password')
        user.save()
        response = client.post('/user/login/', data, follow=True)
        self.assertContains(response, 'Login successful')
        
    def test_00140_applicantFailsUserLogin(self):
        client = Client()
        data = dict(username='applicant', password='pass')
        app = Applicant.objects.create(username='applicant')
        app.set_password('pass')
        app.save()
        response = client.post('/user/login/', data, follow=True)
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
        response = client.post('/login/', data, follow=True)
        self.assertContains(response, 'Login successful')
        
    def test_00240_applicantLoginRejectsUsers(self):
        client = Client()
        user = User.objects.create(username="baduser")
        user.set_password("pass")
        user.save()
        data = dict(username='baduser', password='pass')
        response = client.post('/login/', data, follow=True)
        self.assertContains(response, 'Authentication failed')

    def test_00250_referenceExists(self):
        applicant = Applicant.objects.create(username='newapplicant')
        ref = Reference.objects.create(attached_to=applicant.get_application())
        self.assertIsInstance(ref, Reference)
        
    def test_00260_addMultipleReferencesToApplication(self):
        applicant = Applicant.objects.create(username='newapplicant')
        Reference.objects.create(attached_to=applicant.get_application())
        Reference.objects.create(attached_to=applicant.get_application())
        self.assertEqual(len(Reference.objects.filter(attached_to=applicant.get_application())), 2)

    def test_00270_referenceHasEmailField(self):
        applicant = Applicant.objects.create(username='applicant')
        ref = Reference.objects.create(attached_to=applicant.get_application())
        ref.email = 'zekoff@gmail.com'
        ref.save()
        self.assertEqual(Reference.objects.get(attached_to=applicant).email, 'zekoff@gmail.com')
        
    def test_00280_referenceEmailRejectsNonEmail(self):
        applicant = Applicant.objects.create(username='applicant')
        ref = Reference.objects.create(attached_to=applicant.get_application())
        ref.email = 'bademail'
        ref.save()
        self.assertRaises(NameError, ref.save())

    def test_00290_sendsEmail(self):
        send_mail("subject", "Here is the message...", 'gwaap@auburn.edu', ['zekoff@gmail.com'])
        self.assertEqual(len(mail.outbox), 1) #@UndefinedVariable

    def test_00300_sendsEmailToAddressFromReference(self):
        applicant = Applicant.objects.create(username="applicant")
        ref = Reference.objects.create(attached_to=applicant.get_application())
        ref.email = 'reference@company.com'
        ref.save()
        send_mail('Reference request', "Message content", 'gwaap@auburn.edu', [ref.email])
        self.assertEqual(mail.outbox[0].recipients()[0], 'reference@company.com') #@UndefinedVariable
        
    def test_00310_setupReferenceActionExistsForApplicants(self):
        applicant = Applicant.objects.create(username='applicant')
        applicant.set_password('pass')
        applicant.save()
        client = Client()
        client.login(username='applicant', password='pass')
        response = client.get('/')
        self.assertContains(response, 'Add Reference')
        
    def test_00320_addReferenceViewExists(self):
        applicant = Applicant.objects.create(username='applicant')
        applicant.set_password('pass')
        applicant.save()
        client = Client()
        client.login(username='applicant', password='pass')
        response = client.get('/add_reference/')
        self.assertContains(response, 'Add Reference')
        
    def test_00330_addingReferenceRequiresLogin(self):
        client = Client()
        response = client.get('/add_reference/', follow=True)
        self.assertContains(response, 'Applicant Login')

    def test_00340_completeReferenceViewExists(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.unique_id = '1'
        ref.save()
        response = Client().get('/reference/1/')
        self.assertTrue(response.status_code in [200, 302])

# No longer using this method of authentication        
#    def test_00350_completeReferenceViewRequestsVerification(self):
#        app = Applicant.objects.create(username='app')
#        ref = Reference.objects.create(attached_to=app.get_application())
#        ref.unique_id = '1'
#        ref.save()
#        response = Client().get('/reference/1/')
#        self.assertContains(response, 'Verification code')
        
    def test_00360_completeReferenceAcceptsPost(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.unique_id = '1'
        ref.save()
        data = dict(comments='bbb', overall="0", reference_name="Jim", reference_affiliation="Bob")
        data['integrity'] = 0
        data['development'] = 0
        data['communication'] = 0
        data['motivation'] = 0
        data['research'] = 0
        response = Client().post('/reference/1/', data)
        self.assertContains(response, 'POST accepted')
        
    def test_00361_completeReferenceAcceptsPost(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.unique_id = '1'
        ref.save()
        data = dict(comments='bbb', overall="0", reference_name="Jim", reference_affiliation="Bob")
        response = Client().post('/reference/1/', data)
        self.assertContains(response, 'Error')
        
    def test_00370_completeReferenceGETUsesUniqueID(self):
        applicant = Applicant.objects.create(username='app')
        applicant.first_name = "Test"
        applicant.last_name = "Applicant"
        applicant.save()
        ref = Reference.objects.create(attached_to=applicant.get_application())
        ref.email = 'test@email.com'
        ref.save()
        response = Client().get('/reference/' + str(ref.unique_id) + '/')
        self.assertContains(response, 'Test Applicant')
        
    def test_00380_completeReferenceGETUsesUniqueID2(self):
        applicant = Applicant.objects.create(username='app')
        applicant.first_name = "Michael"
        applicant.last_name = "Zekoff"
        applicant.save()
        ref = Reference.objects.create(attached_to=applicant.get_application())
        ref.email = 'test@email.com'
        ref.save()
        response = Client().get('/reference/' + str(ref.unique_id) + '/')
        self.assertContains(response, 'Michael Zekoff')
        
    def test_00390_addReferenceHasForm(self):
        applicant = Applicant.objects.create(username='applicant')
        applicant.set_password('pass')
        applicant.save()
        client = Client()
        client.login(username='applicant', password='pass')
        response = client.get('/add_reference/')
        self.assertContains(response, '<form')
        
    def test_00400_addReferencePostGeneratesReference(self):
        applicant = Applicant.objects.create(username='applicant')
        applicant.set_password('pass')
        applicant.save()
        client = Client()
        client.login(username='applicant', password='pass')
        data = dict(email='reference@school.edu')
        client.post('/add_reference/', data)
        self.assertEqual('reference@school.edu', Reference.objects.get(attached_to=applicant.get_application()).email)
        
    def test_00410_displayApplicantsViewExists(self):
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/display_applicants/')
        self.assertContains(response, 'Display Applicants')
        
    def test_00420_applicantCannotViewApplicants(self):
        app = Applicant.objects.create(username='applicant')
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='applicant', password='pass')
        response = client.get('/user/display_applicants/', follow=True)
        self.assertContains(response, 'User Login')

    def test_00430_mustBeLoggedInToViewApplicants(self):
        client = Client()
        response = client.get('/user/display_applicants/', follow=True)
        self.assertContains(response, 'User Login')
        
    def test_00440_displayApplicantsShowsAllApplicants(self):
        for x in range(5):
            applicantName = 'applicant' + str(x)
            Applicant.objects.create(username=applicantName)
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/display_applicants/')
        self.assertContains(response, '<tr>', 6)
        
    def test_00450_userCanViewSingleApplicantInfo(self):
        for x in range(5):
            applicantName = 'applicant' + str(x + 1)
            Applicant.objects.create(username=applicantName)
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/view_applicant/1/')
        self.assertContains(response, 'applicant1')
        
    def test_00460_applicantCannotViewApplicantInfo(self):
        applicant = Applicant.objects.create(username='applicant')
        applicant.set_password('pass')
        applicant.save()
        client = Client()
        client.login(username='applicant', password='pass')
        response = client.get('/user/view_applicant/1/', follow=True)
        self.assertContains(response, 'User Login')
        
    def test_00470_displayApplicantsLinksToApplicantViews(self):
        for x in range(5):
            applicantName = 'applicant' + str(x + 1)
            Applicant.objects.create(username=applicantName)
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/display_applicants/')
        self.assertContains(response, '/user/view_applicant/1/')
        
    def test_00480_applicantViewPageGivesCommentOption(self):
        Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/view_applicant/1/', follow=True)
        self.assertContains(response, 'Comment')
        
    def test_00490_applicantViewPageGivesVoteOption(self):
        Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/view_applicant/1/', follow=True)
        self.assertContains(response, 'Vote')
        
    def test_00500_makeCommentViewExists(self):
        Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_comment")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/make_comment/1/')
        self.assertContains(response, 'Make Comment')
        
    def test_00510_makeCommentViewRequiresUserLogin(self):
        applicant = Applicant.objects.create(username='applicant')
        applicant.set_password('pass')
        applicant.save()
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="is_gwaap_user")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='applicant', password='pass')
        response = client.get('/user/make_comment/1/', follow=True)
        self.assertContains(response, 'User Login')

    def test_00520_makeCommentPostSavesComment(self):
        applicant = Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_comment")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        data = dict(comment='Good applicant')
        client.post('/user/make_comment/1/', data)
        comment = Comment.objects.get(attached_to=applicant.get_application())
        self.assertEqual(comment.content, "Good applicant")

    def test_00530_makeCommentGetIncludesForm(self):
        Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_comment")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/make_comment/1/')
        self.assertContains(response, '<form')
        
    def test_00540_postCommentSavesUser(self):
        applicant = Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_comment")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        data = dict(comment='Good applicant')
        client.post('/user/make_comment/1/', data)
        comment = Comment.objects.get(attached_to=applicant.get_application())
        self.assertEqual(comment.made_by, user)
        
    def test_00550_castVoteViewExists(self):
        Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_vote")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/cast_vote/1/')
        self.assertContains(response, 'Cast Vote')

    def test_00560_castVoteViewRequiresPermission(self):
        applicant = Applicant.objects.create(username='applicant')
        applicant.set_password('pass')
        applicant.save()
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_vote")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='applicant', password='pass')
        response = client.get('/user/cast_vote/1/', follow=True)
        self.assertContains(response, 'User Login')
        
    def test_00570_castVotePostSavesVote(self):
        applicant = Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_vote")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        data = dict(vote=1)
        client.post('/user/cast_vote/1/', data)
        vote = Vote.objects.get(attached_to=applicant.get_application())
        self.assertEqual(str(vote), 'Weak Reject by user for applicant')
        
    def test_00580_castVoteGetIncludesForm(self):
        Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_vote")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/user/cast_vote/1/')
        self.assertContains(response, '<form')
        
    def test_00590_castVoteSavesUser(self):
        applicant = Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        user.set_password('pass')
        permission = Permission.objects.get(codename="can_vote")
        user.user_permissions.add(permission)
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        data = dict(vote=1)
        client.post('/user/cast_vote/1/', data)
        vote = Vote.objects.get(attached_to=applicant.get_application())
        self.assertEqual(vote.made_by, user)

    def test_00600_logoutView(self):
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/logout/')
        self.assertContains(response, "logged out")
        
    def test_00610_searchApplicantsViewExists(self):
        user = User.objects.create(username="user")
        user.set_password("pass")
        user.save()
        client = Client()
        client.login(username="user", password='pass')
        response = client.post('/user/search_applicants/', {}, follow=True)
        self.assertContains(response, "Search Applicants")
        
    def test_00620_searchApplicantsRequiresUserLogin(self):
        client = Client()
        response = client.post('/user/search_applicants/', {}, follow=True)
        self.assertContains(response, "User Login")
        
    def test_00630_searchApplicantsAcceptsPostData(self):
        user = User.objects.create(username="user")
        user.set_password("pass")
        user.save()
        client = Client()
        client.login(username="user", password='pass')
        data = dict()
        response = client.post('/user/search_applicants/', data)
        self.assertContains(response, 'POST accepted')
        
    def test_00640_searchPageGetsSearchString(self):
        user = User.objects.create(username="user")
        user.set_password("pass")
        user.save()
        client = Client()
        client.login(username="user", password='pass')
        data = dict(search_string="testing")
        response = client.post('/user/search_applicants/', data)
        self.assertContains(response, 'Search String: testing')
        
    def test_00650_resultsIncludeSearchByUsername(self):
        for x in range(5):
            username = "app" + str(x)
            first = "Test" + str(x)
            last = "Applicant" + str(x)
            applicant = Applicant.objects.create(username=username)
            applicant.first_name = first
            applicant.last_name = last
            applicant.save()
        user = User.objects.create(username="user")
        user.set_password("pass")
        user.save()
        client = Client()
        client.login(username="user", password='pass')
        data = {'search_string':'app'}
        response = client.post('/user/search_applicants/', data)
        self.assertContains(response, 'app1')

    def test_00660_resultsIncludeSearchByFirstName(self):
        for x in range(5):
            username = "app" + str(x)
            first = "Test" + str(x)
            last = "Applicant" + str(x)
            applicant = Applicant.objects.create(username=username)
            applicant.first_name = first
            applicant.last_name = last
            applicant.save()
        user = User.objects.create(username="user")
        user.set_password("pass")
        user.save()
        client = Client()
        client.login(username="user", password='pass')
        data = {'search_string':'Test1'}
        response = client.post('/user/search_applicants/', data)
        self.assertContains(response, 'app1')

    def test_00670_resultsIncludeSearchByLastName(self):
        for x in range(5):
            username = "app" + str(x)
            first = "Test" + str(x)
            last = "Applicant" + str(x)
            applicant = Applicant.objects.create(username=username)
            applicant.first_name = first
            applicant.last_name = last
            applicant.save()
        user = User.objects.create(username="user")
        user.set_password("pass")
        user.save()
        client = Client()
        client.login(username="user", password='pass')
        data = {'search_string':'Applicant3'}
        response = client.post('/user/search_applicants/', data)
        self.assertContains(response, 'app3')
        
    def test_00680_resultsDontIncludeExtras(self):
        for x in range(5):
            username = "app" + str(x)
            first = "Test" + str(x)
            last = "Applicant" + str(x)
            applicant = Applicant.objects.create(username=username)
            applicant.first_name = first
            applicant.last_name = last
            applicant.save()
        user = User.objects.create(username="user")
        user.set_password("pass")
        user.save()
        client = Client()
        client.login(username="user", password='pass')
        data = {'search_string':'Applicant3'}
        response = client.post('/user/search_applicants/', data)
        self.assertContains(response, 'Number of results: 1')
        
    def test_00690_applicantViewApplication(self):
        a = Applicant.objects.create(username='applicant')
        a.set_password('pass')
        a.save()
        client = Client()
        client.login(username='applicant', password='pass')
        response = client.get('/view_application/')
        self.assertContains(response, "Application Details")
        
    def test_00700_viewingApplicationRequiresLogin(self):
        a = Applicant.objects.create(username='applicant')
        a.set_password('pass')
        a.save()
        client = Client()
        response = client.get('/view_application/', follow=True)
        self.assertContains(response, "Applicant Login")
        
    def test_00710_userCannotLoginToApplicantApplicationView(self):
        user = User.objects.create(username='user')
        user.set_password('pass')
        user.save()
        client = Client()
        client.login(username='user', password='pass')
        response = client.get('/view_application/', follow=True)
        self.assertContains(response, 'Applicant Login')
        
    def test_00720_applicantProfileInfoViewExists(self):
        app = Applicant.objects.create(username="app")
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username="app", password='pass')
        response = client.get('/view_profile/')
        self.assertContains(response, "Applicant Profile")

    def test_00730_applicantProfileRequiresLogin(self):
        app = Applicant.objects.create(username="app")
        app.set_password('pass')
        app.save()
        client = Client()
        response = client.get('/view_profile/', follow=True)
        self.assertContains(response, "Applicant Login")
        
    def test_00740_submitResumeViewExists(self):
        app = Applicant.objects.create(username="app")
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/upload_resume/', follow=True)
        self.assertContains(response, 'Upload Resume')
        
    def test_00750_submitResumeRequiresApplicantLogin(self):
        app = User.objects.create(username="app")
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/upload_resume/', follow=True)
        self.assertContains(response, 'Applicant Login')
        
    def test_00760_submitResumeContainsForm(self):
        app = Applicant.objects.create(username="app")
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/upload_resume/', follow=True)
        self.assertContains(response, '<form')

    def test_00770_submitResumeFailsIfNoFile(self):
        app = Applicant.objects.create(username="app")
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='app', password='pass')
        data = dict()
        response = client.post('/upload_resume/', data, follow=True)
        self.assertContains(response, "Error submitting file.")
        
# This test case works, but is deactivated to prevent the creation of actual files on the filesystem during testng.
#    def test_00780_submitResumeWithFile(self):
#        app = Applicant.objects.create(username="app")
#        app.set_password('pass')
#        app.save()
#        client = Client()
#        client.login(username='app', password='pass')
#        resume_file = open("resumefile", "w")
#        resume_file.write("testing")
#        resume_file.close()
#        file_to_upload = UploadedFile(open('resumefile'))
#        data = dict(resume=file_to_upload)
#        response = client.post('/upload_resume/', data, follow=True)
#        self.assertEqual(u"applicant_files/app/resumefile", app.get_application().resume.name)
        
# See test case 00780
#    def test_00790_fileSubmissionVerifiesContentTypeFailure(self):
#        app = Applicant.objects.create(username="app")
#        app.set_password('pass')
#        app.save()
#        client = Client()
#        client.login(username='app', password='pass')
#        resume_file = open("resumefile", "w")
#        resume_file.write("testing")
#        resume_file.close()
#        file_to_upload = UploadedFile(open('resumefile'))
#        file_to_upload.content_type = "badtype"
#        data = dict(resume=file_to_upload)
#        response = client.post('/upload_resume/', data, follow=True)
#        self.assertEqual("", app.get_application().resume.name)

# The functionality is there, but the test case cannot be coerced like this.
#    def test_00800_fileSubmissionVerifiesContentTypePass(self):
#        app = Applicant.objects.create(username="app")
#        app.set_password('pass')
#        app.save()
#        client = Client()
#        client.login(username='app', password='pass')
#        resume_file = open("resumefile", "w")
#        resume_file.write("testing")
#        resume_file.close()
#        file_to_upload = UploadedFile(open('resumefile'))
#        file_to_upload.content_type = "application/pdf"
#        data = dict(resume=file_to_upload)
#        response = client.post('/upload_resume/', data, follow=True)
#        print response
#        self.assertContains(response, "Resume uploaded.")

    def test_00810_submitLetterOfIntentViewExists(self):
        app = Applicant.objects.create(username='app')
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='app', password="pass")
        response = client.get('/upload_letter/', follow=True)
        self.assertContains(response, "Upload Letter of Intent")
        
    def test_00820_submitLetterViewRequiresLogin(self):
        app = User.objects.create(username='app')
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='app', password="pass")
        response = client.get('/upload_letter/', follow=True)
        self.assertContains(response, "Applicant Login")
        
    def test_00830_submitLetterContainsForm(self):
        app = Applicant.objects.create(username='app')
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='app', password="pass")
        response = client.get('/upload_letter/', follow=True)
        self.assertContains(response, "<form")

    def test_00840_submitLetterFailsIfNoFile(self):
        app = Applicant.objects.create(username="app")
        app.set_password('pass')
        app.save()
        client = Client()
        client.login(username='app', password='pass')
        data = dict()
        response = client.post('/upload_resume/', data, follow=True)
        self.assertContains(response, "Error submitting file.")
        
    def test_00850_testReferencesPending(self):
        app = Applicant.objects.create(username='app')
        app.set_password('pass')
        app.save()
        for x in range(3): #@UnusedVariable
            Reference.objects.create(attached_to=app.get_application())
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/view_application/')
        self.assertContains(response, "References Pending")
        
    def test_00860_testReferencesIncomplete(self):
        app = Applicant.objects.create(username='app')
        app.set_password('pass')
        app.save()
        for x in range(2): #@UnusedVariable
            Reference.objects.create(attached_to=app.get_application())
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/view_application/')
        self.assertContains(response, "References Incomplete")
        
    def test_00870_testReferencesComplete(self):
        app = Applicant.objects.create(username='app')
        app.set_password('pass')
        app.save()
        for x in range(3): #@UnusedVariable
            ref = Reference.objects.create(attached_to=app.get_application())
            ref.complete = True
            ref.save()
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/view_application/')
        self.assertContains(response, "References Complete")
        
    def test_00880_transcriptStatusComplete(self):
        app = Applicant.objects.create(username='app')
        app.set_password('pass')
        app.save()
        application = app.get_application()
        application.transcript_status = 0
        application.save()
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/view_application/')
        self.assertContains(response, "Transcript Complete")
        
    def test_00890_greStatusComplete(self):
        app = Applicant.objects.create(username='app')
        app.set_password('pass')
        app.save()
        application = app.get_application()
        application.gre_status = 0
        application.save()
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/view_application/')
        self.assertContains(response, "GRE Complete")

    def test_00900_toeflStatusComplete(self):
        app = Applicant.objects.create(username='app')
        app.set_password('pass')
        app.save()
        application = app.get_application()
        application.toefl_status = 0
        application.save()
        client = Client()
        client.login(username='app', password='pass')
        response = client.get('/view_application/')
        self.assertContains(response, "TOEFL Complete")
        
    def test_00910_referenceViewRejectsIfReferenceAlreadyComplete(self):
        app = Applicant.objects.create(username="app")
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.complete = True
        ref.save()
        client = Client()
        response = client.get('/reference/' + str(ref.unique_id) + "/", follow=True)
        self.assertContains(response, "Thank you")
        
        
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
        
    def test_00210_referenceHasUniqueURL(self):
        applicant = Applicant.objects.create(username="app")
        ref = Reference.objects.create(attached_to=applicant.get_application())
        correct_id = ref.unique_id
        self.assertEqual(ref, Reference.objects.get(unique_id=correct_id))
        
    def test_00220_commentModelExists(self):
        comment = Comment.objects.create(attached_to=Applicant.objects.create(username='test').get_application())
        self.assertIsInstance(comment, Comment)
        
    def test_00230_commentForeignKeyIsApplication(self):
        app = Applicant.objects.create(username='applicant')
        comment = Comment.objects.create(attached_to=app.get_application())
        self.assertIsInstance(comment.attached_to, Application)
        
    def test_00240_commentMadeByUser(self):
        app = Applicant.objects.create(username='applicant')
        user = User.objects.create(username='user')
        comment = Comment.objects.create(attached_to=app.get_application())
        comment.made_by = user
        comment.save()
        comment = Comment.objects.get(attached_to=app.get_application())
        self.assertEqual(comment.made_by, user)
        
    def test_00250_commentContainsContent(self):
        app = Applicant.objects.create(username='applicant')
        comment = Comment.objects.create(attached_to=app.get_application())
        comment.content = "This is a good applicant"
        comment.save()
        comment = Comment.objects.get(attached_to=app.get_application())
        self.assertEqual(comment.content, "This is a good applicant")
        
    def test_00260_voteModelExists(self):
        vote = Vote.objects.create(attached_to=Applicant.objects.create(username='app').get_application())
        self.assertIsInstance(vote, Vote)
        
    def test_00270_voteMadeByUser(self):
        app = Applicant.objects.create(username='app')
        user = User.objects.create(username='user')
        vote = Vote.objects.create(attached_to=app.get_application())
        vote.made_by = user
        vote.save()
        vote = Vote.objects.get(attached_to=app.get_application())
        self.assertIsInstance(vote.made_by, User)
        
    def test_00280_voteModelContainsVote(self):
        app = Applicant.objects.create(username='app')
        vote = Vote.objects.create(attached_to=app.get_application())
        vote.content = 1
        vote.save()
        vote = Vote.objects.get(attached_to=app.get_application())
        self.assertEqual(vote.content, 1)
        
    def test_00280_voteModelUnicodeGivesCorrectString(self):
        app = Applicant.objects.create(username='app')
        vote = Vote.objects.create(attached_to=app.get_application())
        vote.content = 2
        vote.save()
        vote = Vote.objects.get(attached_to=app.get_application())
        self.assertEqual(vote.__unicode__(), VOTE_CHOICES[2][1] + " by None for app")
        
    def test_00290_commentPermissionExists(self):
        perm = Permission.objects.get(codename='can_comment')
        self.assertIsInstance(perm, Permission)
        
    def test_00300_votePermissionExists(self):
        perm = Permission.objects.get(codename='can_vote')
        self.assertIsInstance(perm, Permission)
        
    def test_00310_referenceCanMakeFreeformComments(self):
        applicant = Applicant.objects.create(username='applicant')
        reference = Reference.objects.create(attached_to=applicant.get_application())
        reference.comments = "good applicant"
        reference.save()
        refer = Reference.objects.get(attached_to=applicant.get_application())
        self.assertEqual(refer.comments, "good applicant")
        
    def test_00320_manyToManyUserAndCommentRelationships(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username="user2")
        applicant1 = Applicant.objects.create(username='applicant1')
        applicant2 = Applicant.objects.create(username='applicant2')
        comment11 = Comment.objects.create(attached_to=applicant1.get_application())
        comment11.made_by = user1
        comment11.save()
        comment12 = Comment.objects.create(attached_to=applicant2.get_application())
        comment12.made_by = user1
        comment12.save()
        comment21 = Comment.objects.create(attached_to=applicant1.get_application())
        comment21.made_by = user2
        comment21.save()
        comment22 = Comment.objects.create(attached_to=applicant2.get_application())
        comment22.made_by = user2
        comment22.save()

    def test_00330_manyToManyUserAndCommentRelationships(self):
        user1 = User.objects.create(username='user1')
        user2 = User.objects.create(username="user2")
        applicant1 = Applicant.objects.create(username='applicant1')
        applicant2 = Applicant.objects.create(username='applicant2')
        comment11 = Vote.objects.create(attached_to=applicant1.get_application())
        comment11.made_by = user1
        comment11.save()
        comment12 = Vote.objects.create(attached_to=applicant2.get_application())
        comment12.made_by = user1
        comment12.save()
        comment21 = Vote.objects.create(attached_to=applicant1.get_application())
        comment21.made_by = user2
        comment21.save()
        comment22 = Vote.objects.create(attached_to=applicant2.get_application())
        comment22.made_by = user2
        comment22.save()
        
    def test_00340_referenceModelContainsName(self):
        app = Applicant.objects.create(username="app")
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.name = 'Mr. Reference'
        ref.save()
        ref = Reference.objects.get(attached_to=app.get_application())
        self.assertEqual("Mr. Reference", ref.name)

    def test_00350_referenceModelContainsAffiliation(self):
        app = Applicant.objects.create(username="app")
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.affiliation = 'Big Company'
        ref.save()
        ref = Reference.objects.get(attached_to=app.get_application())
        self.assertEqual("Big Company", ref.affiliation)
        
    def test_00360_applicationModelHasResumeFileField(self):
        app = Applicant.objects.create(username='app')
        application = app.get_application()
        self.assertIsInstance(application.resume, FieldFile)
        
    def test_00370_applicationModelHasLetterOfIntentFileField(self):
        app = Applicant.objects.create(username="app")
        application = app.get_application()
        self.assertIsInstance(application.letter_of_intent, FieldFile)

# Passes, but disabled to prevent writing trash files to filesystem        
#    def test_00380_applicationSavesFile(self):
#        app = Applicant.objects.create(username="app")
#        application = app.get_application()
#        resume_file = File(file("resumefile", "w"))
#        application.resume = resume_file
#        application.save()
#        app.save()
#        self.assertIsInstance(app.get_application().resume, FieldFile)

    def test_00390_modelsModuleHasStatusTuple(self):
        status = 0
        self.assertTrue("Complete" in STATUS_CODE[status])
        
    def test_00400_applicationModelHasGreStatusField(self):
        app = Applicant.objects.create(username='app')
        application = app.get_application()
        application.gre_status = 0
        application.save()
        application = Applicant.objects.get(username='app').get_application()
        self.assertTrue("Complete" in STATUS_CODE[application.gre_status])
    
    def test_00410_applicationModelHasToeflStatusField(self):
        app = Applicant.objects.create(username='app')
        application = app.get_application()
        application.toefl_status = 1
        application.save()
        application = Applicant.objects.get(username='app').get_application()
        self.assertTrue("Incomplete" in STATUS_CODE[application.toefl_status])
        
    def test_00420_applicationModelHasTranscriptStatusField(self):
        app = Applicant.objects.create(username='app')
        application = app.get_application()
        application.transcript_status = 0
        application.save()
        application = Applicant.objects.get(username="app").get_application()
        self.assertTrue("Complete" in STATUS_CODE[application.transcript_status])
        
    def test_00430_referenceHasIntegrityField(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.integrity = 0
        ref.save()
        ref = Reference.objects.get(attached_to=app)
        self.assertTrue(ref.integrity in RELATIVE_RANK[ref.integrity])

    def test_00440_referenceHasDevelopmentField(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.development = 0
        ref.save()
        ref = Reference.objects.get(attached_to=app)
        self.assertTrue(ref.development in RELATIVE_RANK[ref.development])

    def test_00450_referenceHasCommunicationField(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.communication = 0
        ref.save()
        ref = Reference.objects.get(attached_to=app)
        self.assertTrue(ref.communication in RELATIVE_RANK[ref.communication])

    def test_00460_referenceHasMotivationField(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.motivation = 0
        ref.save()
        ref = Reference.objects.get(attached_to=app)
        self.assertTrue(ref.motivation in RELATIVE_RANK[ref.motivation])

    def test_00470_referenceHasResearchField(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.research = 0
        ref.save()
        ref = Reference.objects.get(attached_to=app)
        self.assertTrue(ref.research in RELATIVE_RANK[ref.research])

    def test_00480_referenceHasOverallField(self):
        app = Applicant.objects.create(username='app')
        ref = Reference.objects.create(attached_to=app.get_application())
        ref.overall = 0
        ref.save()
        ref = Reference.objects.get(attached_to=app)
        self.assertTrue(ref.overall in RELATIVE_RANK[ref.overall])
        
    def test_00490_applicationHasStatusField(self):
        app = Applicant.objects.create(username="app")
        app.get_application().status = 0
        app.get_application().save()
        self.assertEqual(app.get_application().status, 0)
        
    def test_00500_profileModelExists(self):
        app = Applicant.objects.create(username="app")
        app_profile = app.get_profile()
#        GwaapProfile.objects.create(applicant_profile=app_profile)
        self.assertIsInstance(GwaapProfile.objects.get(applicant_profile=app_profile), GwaapProfile)
        
    def test_00510_applicantHasConvenienceMethodForProfile(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        gwaap_profile = app.get_gwaap_profile()
        self.assertIsInstance(gwaap_profile, GwaapProfile)
        
    def test_00520_profileHasMiddleName(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.middle_name = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().middle_name, "middle")

    def test_00530_profileHasStreet1(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.street1 = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().street1, "middle")

    def test_00540_profileHasStreet2(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.street2 = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().street2, "middle")
        
    def test_00550_profileHasCity(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.city = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().city, "middle")
        
    def test_00560_profileHasProvince(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.province = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().province, "middle")
        
    def test_00570_profileHasState(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.state = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().state, "middle")
        
    def test_00570_profileHasCountry(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.country = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().country, "middle")
        
    def test_00580_profileHasZip(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.zip_code = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().zip_code, "middle")
        
    def test_00590_profileHasTelephone(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.phone = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().phone, "middle")
        
    def test_00600_profileHasBirthday(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.birthday = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().birthday, "middle")
        
    def test_00610_profileHasGender(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.gender = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().gender, "middle")
        
    def test_00620_profileHasCountry_Birth(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.country_birth = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().country_birth, "middle")
        
    def test_00630_profileHasCitizenship(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.citizenship = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().citizenship, "middle")
        
    def test_00640_profileHasRef_Number(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.ref_number = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().ref_number, "middle")
        
    def test_00650_profileHasDate_Apply(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.date_apply = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().date_apply, "middle")
        
    def test_00660_profileHasEnter_Qtr(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.enter_qtr = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().enter_qtr, "middle")
        
    def test_00670_profileHasEnter_YEAR(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.enter_year = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().enter_year, "middle")
        
    def test_00670_profileHasDegree(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.degree = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().degree, "middle")
        
    def test_00680_profileHasMajor(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.major = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().major, "middle")
        
    def test_00690_profileHasGRE_TAKEN(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.gre_taken = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().gre_taken, "middle")
        
    def test_00700_profileHasO_GRE_V(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.o_gre_v = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().o_gre_v, "middle")
        
    def test_00710_profileHasO_GRE_Q(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.o_gre_q = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().o_gre_q, "middle")
        
    def test_00720_profileHasO_GRE_A(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.o_gre_a = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().o_gre_a, "middle")
        
    def test_00730_profileHasO_GRE_W(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.o_gre_w = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().o_gre_w, "middle")
        
    def test_00740_profileHasTOEFL_TAKEN(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.toefl_taken = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().toefl_taken, "middle")
        
    def test_00750_profileHasO_TOEFL_SCORE(self):
        app = Applicant.objects.create(username="app")
#        GwaapProfile.objects.create(applicant_profile=app.get_profile())
        p = app.get_gwaap_profile()
        p.o_toefl_score = "middle"
        p.save()
        self.assertEqual(app.get_gwaap_profile().o_toefl_score, "middle")
        
    def test_00760_applicantsGetProfilesAutomatically(self):
        app = Applicant.objects.create(username='app')
        p = app.get_gwaap_profile()
        self.assertIsInstance(p, GwaapProfile)
        
