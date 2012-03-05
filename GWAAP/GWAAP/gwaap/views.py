# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User
from django.contrib.auth.decorators import permission_required

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
    return HttpResponse(content="User Login")
