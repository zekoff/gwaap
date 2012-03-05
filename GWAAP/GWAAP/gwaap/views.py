# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login

#def pagetest(request):
#    return HttpResponse(content="Pagetest")
#
#def logintest(request):
#    form = AuthenticationForm()
#    return HttpResponse(form.__unicode__())
#
#def sandboxbranchview(request):
#    return HttpResponse(content="This is the sandbox")

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
    return HttpResponse('Applicant Home')

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

