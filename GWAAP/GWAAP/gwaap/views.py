# Create your views here.
from django.http import HttpResponse
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login
from GWAAP.gwaap.models import Reference, Application, Applicant, Comment, User, \
    Vote

@permission_required('gwaap.is_gwaap_user', login_url="/user/login/")
def userActions(request):
    page_content = '''
    <h1>User Actions</h1>
    <a href='/user/display_applicants/'>Display Applicants</a>
    '''
    return HttpResponse(content=page_content)

def userLogin(request):
    if request.method == 'POST':
        name = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(username=name, password=pwd)
        if user is not None:
            if not user.has_perm('gwaap.is_gwaap_user'):
                return HttpResponse("Authentication failed.")
            login(request, user)
            page_content = "Logged in " + str(user.username)
            page_content += "\n<a href='/user/'>Go to User Actions page</a>"
            return HttpResponse(page_content)
        return HttpResponse("Authentication failed.")
    page_content = '''
    <form action='/user/login/' method='post'>
    <p>User Login</p>
    <input type='text' name='username' />
    <input type='password' name='password' />
    <input type='submit' />
    </form>
    '''
    return HttpResponse(content=page_content)

@permission_required('gwaap.is_gwaap_user', login_url='/user/login/')
def displayApplicants(request):
    page_content = '''
    <h1>Applicants</h1>
    <!-- Display Applicants -->
    '''
    for applicant in Applicant.objects.all():
        page_content += '<a href="/user/view_applicant/' + str(applicant.pk) + '/">' + str(applicant) + '</a><br />'
    return HttpResponse(content=page_content)

@permission_required('gwaap.is_gwaap_user', login_url='/user/login/')
def viewApplicant(request, applicant_pk):
    page_content = '''
    <h1>Applicant Information</h1>
    '''
    applicant = Applicant.objects.get(pk=applicant_pk)
    page_content += '<p>' + str(applicant) + '</p>'
    page_content += "<a href='/user/make_comment/" + str(applicant_pk) + "/'>Make Comment</a>"
    page_content += "<br />"
    page_content += "<a href='/user/cast_vote/" + str(applicant_pk) + "/'>Cast Vote</a>"
    return HttpResponse(content=page_content)

@permission_required('gwaap.is_gwaap_applicant', login_url='/login/')
def applicantHome(request):
    page_content = '''
    <h1>Applicant Home</h1>
    <a href='/add_reference/'>Add Reference</a>
    '''
    return HttpResponse(page_content)

def applicantLogin(request):
    if request.method == "POST":
        name = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(username=name, password=pwd)
        if user is not None:
            if not user.has_perm('gwaap.is_gwaap_applicant'):
                return HttpResponse("Authentication failed.")
            login(request, user)
            page_content = "Logged in " + str(user.username)
            page_content += "\n<a href='/'>Go to Applicant Homepage</a>"
            return HttpResponse(page_content)
    page_content = '''
    <form action='/login/' method='post'>
    <p>Applicant Login</p>
    <input type='text' name='username' />
    <input type='password' name='password' />
    <input type='submit' />
    </form>
    '''
    return HttpResponse(page_content)

@permission_required('gwaap.is_gwaap_applicant', login_url='/login/')
def applicantAddReference(request):
    if request.method == 'POST':
        application = Application.objects.get(applicant_profile=request.user.get_profile())
        ref = Reference.objects.create(attached_to=application)
        ref.email = request.POST['email']
        ref.save()
        page_content = '''
        <h1>Add Reference</h1>
        <p>Reference added and email sent to:</p>
        '''
        page_content += '<p><strong>' + str(ref.email) + '</strong></p>'
        page_content += '<a href="/">Back to Home</a>'
        return HttpResponse(page_content)
    page_content = '''
    <h1>Add Reference</h1>
    <form action='/add_reference/' method='post'>
    <p>Email address for reference:</p>
    <input type='text' name='email' />
    <input type='submit' />
    </form>
    '''
    return HttpResponse(page_content)

def completeReference(request, unique_id):
    reference = Reference.objects.get(unique_id=unique_id) # this will cause an error if no one is found
    application = reference.attached_to
    profile = application.applicant_profile
    applicant = profile.user
    if request.method == "POST":
        reference.comments = request.POST['comments']
        reference.save()
        page_content = '<h1>Reference Complete for ' + str(applicant.get_full_name()) + '</h1><!-- POST accepted -->'
        return HttpResponse(page_content)
    page_content = "<h1>Complete Reference for " + str(applicant.get_full_name()) + "</h1><form action='"
    page_content += str(request.path)
    page_content += '''' method='post'>
    <p>Describe your experience with this applicant:</p>
    <input type='text' name='comments' />
    <input type='submit' />
    </form>
    '''
    return HttpResponse(page_content)

@permission_required('gwaap.can_comment', login_url='/user/login/')
def makeComment(request, applicant_pk):
    applicant = Applicant.objects.get(pk=applicant_pk)
    if request.method == "POST":
        comment = Comment.objects.create(attached_to=applicant.get_application())
        comment.content = request.POST['comment']
        comment.made_by = User.objects.get(username=request.user.username)
        comment.save()
        page_content = "<p>Comment posted for " + str(applicant) + "</p>"
        return HttpResponse(content=page_content) 
    page_content = "<h1>Make Comment</h1>"
    page_content += "<p>Commenting on " + str(applicant) + "</p>"
    page_content += '<form method="POST" action="/user/make_comment/' + str(applicant_pk) + '/">'
    page_content += '''<input name="comment" type="text" /><input type="submit" /></form>'''
    return HttpResponse(content=page_content)

@permission_required('gwaap.can_vote', login_url='/user/login/')
def castVote(request, applicant_pk):
    applicant = Applicant.objects.get(pk=applicant_pk)
    if request.method == "POST":
        pass
        vote = Vote.objects.create(attached_to=applicant.get_application())
        vote.content = request.POST['vote']
        user = User.objects.get(username=request.user.username)
        vote.made_by = user
        vote.save()
        page_content = "Vote cast for " + str(applicant)
        return HttpResponse(content=page_content)
    page_content = "<h1>Cast Vote</h1>"
    page_content += "<form method='POST' action='/user/cast_vote/" + str(applicant_pk) + "/'>"
    page_content += '''<input name='vote' type='text' /><input type='submit' /></form>'''
    return HttpResponse(content=page_content)
