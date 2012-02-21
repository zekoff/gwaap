# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.forms import AuthenticationForm
from django.contrib.auth.models import User

#def pagetest(request):
#    return HttpResponse(content="Pagetest")
#
#def logintest(request):
#    form = AuthenticationForm()
#    return HttpResponse(form.__unicode__())
#
#def sandboxbranchview(request):
#    return HttpResponse(content="This is the sandbox")

def userActions(request):
    try:
        if User.objects.get(username=request.user.username):
#    if request.user.is_authenticated():
            return HttpResponse(content='User Actions')
    except:
        return HttpResponseRedirect('/user/login/')
    else:
        return HttpResponseRedirect('/user/login/')
