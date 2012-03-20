# Create your views here.
from django.http import HttpResponse, HttpResponseRedirect
from django.contrib.auth.decorators import permission_required
from django.contrib.auth import authenticate, login, logout
from GWAAP.gwaap.models import Reference, Application, Applicant, Comment, User, \
    Vote
from django.shortcuts import render_to_response
from django.contrib import messages
from django.template.context import RequestContext

@permission_required('gwaap.is_gwaap_user', login_url="/user/login/")
def userActions(request):
    return render_to_response('user_templates/user_home.html', {}, RequestContext(request))

def userLogin(request):
    if request.method == 'POST':
        name = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(username=name, password=pwd)
        if user is None or not user.has_perm('gwaap.is_gwaap_user') :
            messages.error(request, "Authentication failed.")
            return HttpResponseRedirect("/user/login/")
        login(request, user)
        messages.success(request, "Login successful.")
        return HttpResponseRedirect('/user/')
    return render_to_response('user_templates/user_login.html', {}, RequestContext(request))

@permission_required('gwaap.is_gwaap_user', login_url='/user/login/')
def displayApplicants(request):
    data = dict(applicant_list=Applicant.objects.all())
    return render_to_response('user_templates/display_applicants_template.html', data, RequestContext(request))

@permission_required('gwaap.is_gwaap_user', login_url='/user/login/')
def viewApplicant(request, applicant_pk):
    data = dict(applicant=Applicant.objects.get(pk=applicant_pk))
    return render_to_response('user_templates/view_applicant_template.html', data, RequestContext(request))

@permission_required('gwaap.is_gwaap_applicant', login_url='/login/')
def applicantHome(request):
    return render_to_response('applicant_templates/applicant_home_template.html', {}, RequestContext(request))

def applicantLogin(request):
    if request.method == "POST":
        name = request.POST['username']
        pwd = request.POST['password']
        user = authenticate(username=name, password=pwd)
        if user is None or not user.has_perm('gwaap.is_gwaap_applicant'):
            messages.error(request, "Authentication failed.")
            return HttpResponseRedirect("/")
        login(request, user)
        messages.success(request, "Login successful.")
        return HttpResponseRedirect('/')
    return render_to_response('applicant_templates/applicant_login_template.html', {}, RequestContext(request))

@permission_required('gwaap.is_gwaap_applicant', login_url='/login/')
def applicantAddReference(request):
    if request.method == 'POST':
        application = Application.objects.get(applicant_profile=request.user.get_profile())
        ref = Reference.objects.create(attached_to=application)
        ref.email = request.POST['email']
        ref.save()
        messages.success(request, "Reference added.")
        messages.info(request, "Email sent to " + str(request.POST['email']))
        return HttpResponseRedirect('/add_reference/')
    return render_to_response('applicant_templates/add_reference_template.html', {}, RequestContext(request))

def completeReference(request, unique_id):
    reference = Reference.objects.get(unique_id=unique_id) # this will cause an error if no one is found
    application = reference.attached_to
    profile = application.applicant_profile
    applicant = profile.user
    data = dict(applicant=applicant)
    if request.method == "POST":
        reference.comments = request.POST['comments']
        reference.save()
        return render_to_response('reference_complete.html', data, RequestContext(request))
    return render_to_response('reference_template.html', data, RequestContext(request))

@permission_required('gwaap.is_gwaap_user', login_url='/user/login/')
def makeComment(request, applicant_pk):
    # Need to check if Comment for this Applicant already exists by this User
    if not request.user.has_perm("gwaap.can_comment"):
        messages.error(request, "You do not have permission to make comments on applications.")
        return HttpResponseRedirect('/user/')
    applicant = Applicant.objects.get(pk=applicant_pk)
    data = dict(applicant=applicant)
    if request.method == "POST":
        comment = Comment.objects.create(attached_to=applicant.get_application())
        comment.content = request.POST['comment']
        comment.made_by = User.objects.get(username=request.user.username)
        comment.save()
        messages.success(request, "Comment recorded for " + str(applicant.get_full_name()))
        return HttpResponseRedirect('/user/view_applicant/' + str(applicant_pk) + '/')
    return render_to_response('user_templates/make_comment.html', data, RequestContext(request))

@permission_required('gwaap.is_gwaap_user', login_url='/user/login/')
def castVote(request, applicant_pk):
    # Need to check if Vote for this Applicant already exists by this User
    if not request.user.has_perm("gwaap.can_vote"):
        messages.error(request, "You do not have permission to vote on applications.")
        return HttpResponseRedirect('/user/')
    applicant = Applicant.objects.get(pk=applicant_pk)
    data = dict(applicant=applicant)
    if request.method == "POST":
        vote = Vote.objects.create(attached_to=applicant.get_application())
        vote.content = int(request.POST['vote'])
        vote.made_by = User.objects.get(username=request.user.username)
        vote.save()
        messages.success(request, "Vote cast for " + str(applicant.get_full_name()))
        return HttpResponseRedirect('/user/view_applicant/' + str(applicant.pk) + '/')
    return render_to_response('user_templates/cast_vote.html', data, RequestContext(request))

def logoutView(request):
    logout(request)
    return render_to_response('logout_template.html', {})

def testView(request):
    return render_to_response('base_template.html', {})
