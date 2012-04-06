'''
Created on Apr 4, 2012

@author: Zekoff
'''
from random import choice
from gwaap.models import Applicant, User
from django.contrib.auth.models import Permission
from GWAAP.gwaap.models import Reference

first_names = "Joe John Albert David Jim Tim Dawn Oscar Michael David Phyllis Meredith Kelly Lauren Mark Nathan Ryan Kevin Timothy Bill William"
last_names = "Clinton Smith Thomas Walker Bush Johnson Smithson Thompson Fillion Frederick Holworth Carlisle Wallace Churchill Gregory"

if __name__ == '__main__':
    first_names = first_names.split()
    last_names = last_names.split()
    for x in range(100):
        first = choice(first_names)
        last = choice(last_names)
        un = str(first[0] + last).lower() + str(x)
        app = Applicant.objects.create(username=un)
        app.first_name = first
        app.last_name = last
        app.set_password('pass')
        app.save()
        print "Filler applicant created: " + str(app)
    user = User.objects.create(username="facultyMember")
    user.set_password("pass")
    perm = Permission.objects.get(codename='can_comment')
    user.user_permissions.add(perm)
    user.save()
    user = User.objects.create(username="anotherFaculty")
    user.set_password("pass")
    perm = Permission.objects.get(codename='can_comment')
    user.user_permissions.add(perm)
    perm = Permission.objects.get(codename='can_vote')
    user.user_permissions.add(perm)
    user.save()
    print "Faculty members created: " + str(User.objects.all())
    app = Applicant.objects.create(username="jsmith")
    app.first_name = "John"
    app.last_name = "Smith"
    app.set_password('pass')
    app.email = "johnsmith@gmail.com"
    app.save()
    a = app.get_gwaap_profile()
    a.street1 = "123 Oak Lane"
    a.street2 = "Apt 45"
    a.city = "Auburn"
    a.state = "AL"
    a.country = "USA"
    a.zip = "36830"
    a.phone = "555-645-3462"
    a.birthday = "15 January 1990"
    a.gender = "M"
    a.country_birth = "USA"
    a.citizenship = "USA"
    a.ref_number = "59493389329423"
    a.date_apply = "27 March 2012"
    a.enter_qtr = "FALL"
    a.enter_year = "2012"
    a.degree = "Master"
    a.major = "SwEng"
    a.gre_taken = "NO"
    a.toefl_taken = "N/A"
    a.save()
    appl = app.get_application()
    appl.toefl_status = 5
    appl.gre_status = 0
    appl.transcript_status = 0
    appl.save()
    for x in range(2):
        ref = Reference.objects.create(attached_to=appl)
    print "Sample user created: " + str(app)
