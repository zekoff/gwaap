# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login
from GWAAP.gwaap.models import Reference, Applicant, Application

@permission_required('gwaap.is_gwaap_user', login_url="/user/login/")
def userActions(request):
    return HttpResponse(content='User Actions')

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

@permission_required('gwaap.is_gwaap_applicant', login_url='/login/')
def applicantHome(request):
    page_content = '''
    <h1>Applicant Home</h1>
    <a href='/'>Add Reference</a>
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
        page_content = '<h1>Complete Reference for ' + str(applicant.get_full_name()) + '</h1><!-- POST accepted -->'
        return HttpResponse(page_content)
    page_content = "<h1>Complete Reference for " + str(applicant.get_full_name()) + "</h1><form action='"
    page_content += str(request.path)
    page_content += '''' method='post'>
    <p>Verification code:</p>
    <input type='text' name='verification_code' />
    <input type='submit' />
    </form>
    '''
    return HttpResponse(page_content)

