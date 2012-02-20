# Create your views here.
from django.shortcuts import render_to_response
from django.http import HttpResponse
from django.contrib.auth.forms import AuthenticationForm

def pagetest(request):
    return HttpResponse(content="Pagetest")

def logintest(request):
    form = AuthenticationForm()
    return HttpResponse(form.__unicode__())
