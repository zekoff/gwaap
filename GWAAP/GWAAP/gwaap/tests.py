"""
This file demonstrates writing tests using the unittest module. These will pass
when you run "manage.py test".

Replace this with more appropriate tests for your application.
"""

from django.test import TestCase
from models import User
from models import Applicant
from models import Application

#class SimpleTest(TestCase):
#    def test_basic_addition(self):
#        """
#        Tests that 1 + 1 always equals 2.
#        """
#        self.assertEqual(1 + 1, 2)

class ModelTests(TestCase):
    
    def test_0010_userExists(self):
        user = User()
        self.assertIsInstance(user, User)
    
    def test_0020_userHasUsername(self):
        user = User()
        self.assertEqual(user.username, '')
        
    def test_0030_userNameWorks(self):
        user = User()
        user.first_name = "Joe"
        user.last_name = "Tester"
        self.assertEqual(user.get_full_name(), "Joe Tester")

    def test_0040_userPassword(self):
        user = User()
        user.set_password("password42")
        self.assertTrue(user.check_password("password42"))
        
    def test_0050_applicantExists(self):
        applicant = Applicant()
        self.assertIsInstance(applicant, Applicant)
        
    def test_0060_applicationExists(self):
        app = Application()
        self.assertIsInstance(app, Application)
        
#    def test_0070_applicationHasNameField(self):
#        app = Application()
#        name = app.name
#        print name
#        self.assertEqual(name, "")

    def test_0071_applicationHasApplicantForeignKey(self):
        app = Application()
        applicant = Applicant()
        applicant.save()
        app.owner = applicant
        app.save()
        app = Application.objects.get(pk=1)
        self.assertEqual(applicant, app.owner)
