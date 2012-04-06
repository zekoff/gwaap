# Create your views here.
from GWAAP.gwaap.models import Reference, Application, Applicant, Comment, User, \
    Vote, VOTE_CHOICES
from django.contrib import messages
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import permission_required
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render_to_response
from django.template.context import RequestContext
from django.core.mail import send_mail

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
    user = User.objects.get(pk=request.user.pk)
    applicant = Applicant.objects.get(pk=applicant_pk)
    profile = applicant.get_gwaap_profile()
    application = applicant.get_application()
    data = dict()
    data['extra_onready_js'] = "$('#appTab').tab('show');"
    data['user'] = user
    data['applicant'] = applicant
    data['profile'] = profile
    data['application'] = application
    data['comments'] = Comment.objects.filter(attached_to=application)
    data['references'] = Reference.objects.filter(attached_to=application).filter(complete=True)
    profile_fields = []
    profile_fields.append("<td><strong>EMAIL</strong></td><td>" + str(applicant.email) + "</td>")
    profile_fields.append("<td><strong>FIRST_NAME</strong></td><td>" + str(applicant.first_name) + "</td>")
    profile_fields.append("<td><strong>LAST_NAME</strong></td><td>" + str(applicant.last_name) + "</td>")
    for field in profile._meta.fields:
        if field.name in ['id', 'applicant_profile']: continue
        to_append = "<td><strong>"
        to_append += str(field.name).upper()
        to_append += "</strong></td><td>"
        to_append += str(getattr(profile, str(field.name)))
        profile_fields.append(to_append)
    data['profile_fields'] = profile_fields
    return render_to_response('user_templates/view_applicant_template.html', data, RequestContext(request))

@permission_required('gwaap.is_gwaap_applicant', login_url='/login/')
def applicantHome(request):
    data = dict()
    applicant = Applicant.objects.get(pk=request.user.pk)
    application = applicant.get_application()
    data['progress_bar_width'] = str(100.0 / 6 * application.status + 100.0 / 12) + "%"
    if application.status == 5:
        data['progress_bar_width'] = "100%"
    data['applicant'] = applicant
    bold_cell = "status_" + str(application.status)
    data[bold_cell] = "gwaap_bold_cell"
    application_complete = True
    if application.transcript_status != 0:
        application_complete = False
    if not application.letter_of_intent:
        application_complete = False
    if not application.resume:
        application_complete = False
    if application.gre_status != 0:
        application_complete = False
    if application.toefl_status not in [0, 5]:
        application_complete = False
    if len(Reference.objects.filter(attached_to=application)) < 3:
        application_complete = False
    if application_complete:
        data['application_complete'] = True
    else:
        data['application_complete'] = False
    return render_to_response('applicant_templates/applicant_home_template.html', data, RequestContext(request))

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
    applicant = Applicant.objects.get(pk=request.user.pk)
    application = applicant.get_application()
    if len(Reference.objects.filter(attached_to=application)) >= 3:
        messages.info(request, "All three reference requests have already been sent.")
        return HttpResponseRedirect('/view_application/')
    if request.method == 'POST':
        application = Application.objects.get(applicant_profile=request.user.get_profile())
        ref = Reference.objects.create(attached_to=application)
        ref.email = request.POST['email']
        ref.save()
        gwaap_address = "http://gwaap.auburn.edu/"
        email_message = '''
        To whom it may concern:
        
        A request that you serve as a reference has been made by an applicant to the graduate program
        in the Auburn University Computer Science and Software Engineering department. Clicking the 
        link below will take you to the recommendation form on the CSSE graduate application website.
        The form consists of six multiple-choice questions asking you to describe your experience with
        the applicant, as well as an optional box for additional comments.
        
        Your comments will not be seen by the applicant at any time, and the form can be completed in
        less than two minutes.
        
        Thank you in advance for your contribution to the process of evaluating applicants here at
        Auburn University. Details on the applicant and a link to the form can be found below:
        
        '''
        email_message += "Applicant name: " + str(applicant.get_full_name())
        email_message += "\nLink to private recommendation form: " + gwaap_address + "reference/" + str(ref.unique_id) + "/"
        send_mail("Recommendation request from " + applicant.get_full_name(), email_message, 'gwaap@auburn.edu', [ref.email])
        messages.success(request, "Reference added.")
        messages.info(request, "Email sent to " + str(request.POST['email']))
        return HttpResponseRedirect('/view_application/')
    return render_to_response('applicant_templates/add_reference_template.html', {}, RequestContext(request))

def completeReference(request, unique_id):
    reference = Reference.objects.get(unique_id=unique_id) # this will cause an error if no one is found
    if reference.complete:
        messages.info(request, "You have already filled out a reference for this applicant. If you believe you are receiving this message in error, contact the AU CSSE department.")
        return render_to_response('reference_complete.html', {}, RequestContext(request))
    application = reference.attached_to
    profile = application.applicant_profile
    applicant = profile.user
    data = dict(applicant=applicant)
    if request.method == "POST":
        # Ensure that reference has at least filled out overall recommendation
        if not request.POST['overall']:
            messages.error(request, "You are required to make an overall recommendation on this applicant to complete the form.")
            return render_to_response('reference_template.html', data, RequestContext(request))
        # Save all responses in the database
        reference.complete = True
        try:
            reference.overall = int(request.POST['overall'])
            reference.comments = request.POST['comments']
            if request.POST['reference_name']:
                reference.name = request.POST['reference_name']
            if request.POST['reference_affiliation']:
                reference.affiliation = request.POST['reference_affiliation']
            reference.integrity = int(request.POST['integrity'])
            reference.development = int(request.POST['development'])
            reference.communication = int(request.POST['communication'])
            reference.motivation = int(request.POST['motivation'])
            reference.research = int(request.POST['research'])
        except:
            messages.error(request, "Error saving responses in database.")
            return render_to_response('reference_template.html', data, RequestContext(request))
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
    if not request.user.has_perm("gwaap.can_vote"):
        messages.error(request, "You do not have permission to vote on applications.")
        return HttpResponseRedirect('/user/')
    # Need to check if Vote for this Applicant already exists by this User
    applicant = Applicant.objects.get(pk=applicant_pk)
    user = User.objects.get(pk=request.user.pk)
    data = dict(applicant=applicant)
    existing_vote = Vote.objects.filter(attached_to=applicant.get_application()).filter(made_by=user)
    if request.method == "POST":
        if len(existing_vote) == 0:
            vote = Vote.objects.create(attached_to=applicant.get_application())
        else:
            vote = Vote.objects.filter(attached_to=applicant.get_application()).filter(made_by=user)[0]
        vote.content = int(request.POST['vote'])
        vote.made_by = User.objects.get(username=request.user.username)
        vote.save()
        messages.success(request, "Vote cast for " + str(applicant.get_full_name()))
        return HttpResponseRedirect('/user/view_applicant/' + str(applicant.pk) + '/')
    if len(existing_vote) > 0:
        messages.info(request, "You have already voted on this applicant. This vote will override your previous one.")
    data['vote_choices'] = []
    for choice in VOTE_CHOICES:
        data['vote_choices'].append("<option value='" + str(choice[0]) + "'>" + str(choice[1]) + "</option>")
    return render_to_response('user_templates/cast_vote.html', data, RequestContext(request))

def logoutView(request):
    logout(request)
    return render_to_response('logout_template.html', {}, RequestContext(request))

# Can/should be removed after debugging
def testView(request):
    return render_to_response('base_template.html', {})

@permission_required('gwaap.is_gwaap_user', login_url='/user/login/')
def searchApplicants(request):
    data = dict(method=request.method)
    data['search_string'] = None
    if 'search_string' in request.POST:
        data['search_string'] = request.POST['search_string']
    search_terms = []
    if data['search_string']:
        search_terms = data['search_string'].split()
    data['search_terms_list'] = search_terms
    results = []
    for applicant in Applicant.objects.all():
        exclude = False
        for term in search_terms:
            term = term.lower()
            if applicant.username.lower().find(term) == -1 and applicant.get_full_name().lower().find(term) == -1:
                exclude = True
        if not exclude:
            results.append(applicant)
    data['applicant_list'] = results
    return render_to_response("user_templates/search_applicants.html", data, RequestContext(request))

# Define status cell content options
COMPLETE_CELL = '''<td style="background-color: #468847"><i class="icon-ok icon-white"></i></td>'''
INCOMPLETE_CELL = '''<td style="background-color: #B94A48"><i class="icon-remove icon-white"></i></td>'''
PENDING_CELL = '''<td style="background-color: #F89406"><i class="icon-time icon-white"></i></td>'''
NA_CELL = '''<td style="background-color: #999999">N/A</td>'''

# Define button content options
NO_ACTION = '''<a class="btn disabled">None</a>'''
def details_button(css_id):
    return "<button data-original-title='Details' class='btn btn-info' id='" + str(css_id) + "'><i class='icon-search icon-white'></i> Details</button>"
def details_js(css_id, content):
    return "$('#" + str(css_id) + "').popover({content: '" + str(content) + "', placement:'left'});"

@permission_required('gwaap.is_gwaap_applicant', login_url='/login/')
def viewApplication(request):
    data = dict()
    applicant = Applicant.objects.get(pk=request.user.pk)
    application = applicant.get_application()
    problem_with_application = False
    data['extra_comments'] = ''
    data['extra_onready_js'] = ''
    # Fill context dict with status reports and relevant actions
    data['online_application_status'] = COMPLETE_CELL
    data['online_application_actions'] = NO_ACTION
    # Transcripts
    data['transcripts_status'] = INCOMPLETE_CELL
    data['transcripts_actions'] = NO_ACTION
    if application.transcript_status == 0:
        data['transcripts_status'] = COMPLETE_CELL
        data['extra_comments'] += "Transcript Complete"
    elif application.transcript_status == 6:
        problem_with_application = True
    else:
        transcripts_button = "transcripts_detail_button"
        data['transcripts_actions'] = details_button(transcripts_button)
        detail_content = "Transcripts not yet received by Graduate School."
        data['extra_onready_js'] += details_js(transcripts_button, detail_content)
    # GRE scores
    data['gre_scores_status'] = INCOMPLETE_CELL
    data['gre_scores_actions'] = NO_ACTION
    if application.gre_status == 0:
        data['gre_scores_status'] = COMPLETE_CELL
        data['extra_comments'] += "GRE Complete"
    elif application.gre_status == 6:
        problem_with_application = True
    else:
        gre_button = "gre_detail_button"
        data['gre_scores_actions'] = details_button(gre_button)
        detail_content = "GRE scores not yet received by Graduate School."
        data['extra_onready_js'] += details_js(gre_button, detail_content)
    # TOEFL scores
    data['toefl_scores_status'] = INCOMPLETE_CELL
    data['toefl_scores_actions'] = NO_ACTION
    if application.toefl_status == 0:
        data['toefl_scores_status'] = COMPLETE_CELL
        data['extra_comments'] += "TOEFL Complete"
    elif application.toefl_status == 6:
        problem_with_application = True
    elif application.toefl_status == 5:
        data['toefl_scores_status'] = NA_CELL
    # References
    data['references_status'] = INCOMPLETE_CELL
    data['references_actions'] = NO_ACTION
    num_references = len(Reference.objects.filter(attached_to=application))
    if num_references < 3:
        data['references_status'] = INCOMPLETE_CELL
        button_id = "references_detail_button"
        data['references_actions'] = '''<a class="btn btn-primary" href="/add_reference/"><i class="icon-pencil icon-white"></i> Add Reference</a> ''' + details_button(button_id)
        data['extra_comments'] += "References Incomplete"
        details_content = "References requested: " + str(num_references) + "/3.<br/>You must receive recommendations from 3 references."
        data['extra_onready_js'] += details_js(button_id, details_content)
    else:
        references = Reference.objects.filter(attached_to=application)
        references_pending = False
        for reference in references:
            if not reference.complete:
                references_pending = True
        if references_pending:
            data['extra_comments'] += "References Pending"
            data['references_status'] = PENDING_CELL
            button_id = "references_detail_button"
            data['references_actions'] = details_button(button_id)
            details_content = "Awaiting replies from references."
            data['extra_onready_js'] += details_js(button_id, details_content)
        else:
            data['extra_comments'] += "References Complete"
            data['references_status'] = COMPLETE_CELL
    # Resume
    data['resume_status'] = INCOMPLETE_CELL
    data['resume_actions'] = NO_ACTION
    if application.resume:
        data['resume_status'] = COMPLETE_CELL
        data['resume_actions'] = '''<a class='btn' href='/upload_resume/'><i class='icon-retweet'></i> Resubmit</a>'''
    if not application.resume:
        data['resume_actions'] = '''<a class='btn btn-primary' href='/upload_resume/'><i class='icon-file icon-white'></i> Upload Resume</a>'''
    # Letter of intent
    data['letter_status'] = INCOMPLETE_CELL
    data['letter_actions'] = NO_ACTION
    if application.letter_of_intent:
        data['letter_status'] = COMPLETE_CELL
        data['letter_actions'] = '''<a class='btn' href='/upload_letter/'><i class='icon-retweet'></i> Resubmit</a>'''
    if not application.letter_of_intent:
        data['letter_actions'] = '''<a class='btn btn-primary' href='/upload_letter/'><i class='icon-file icon-white'></i> Upload Letter of Intent</a>'''
        
    if problem_with_application:
        messages.error(request, "There is a problem with your application. Please contact the CSSE Graduate Officer.")
    return render_to_response('applicant_templates/view_application_template.html', data, RequestContext(request))

def form_field(placeholder="EMPTY", disabled=True, name=""):
    css_class = "x-large"
    if disabled:
        css_class += " disabled"
    control = "<input class='" + css_class + "' value='" + str(placeholder) + "' type='text' "
    if disabled:
        control += "disabled "
    if name:
        control += "name='" + str(name) + "' "
    control += "/>"
    return control

@permission_required('gwaap.is_gwaap_applicant', login_url='/login/')
def viewProfile(request):
    data = dict()
    applicant = Applicant.objects.get(pk=request.user.pk)
    profile = applicant.get_gwaap_profile()
    application = applicant.get_application()
    if request.method == "POST":
        # Check for updates to selected fields, update if necessary
        if profile.street1 != request.POST['street1']: profile.street1 = request.POST['street1']
        if profile.street2 != request.POST['street2']: profile.street2 = request.POST['street2']
        if profile.city != request.POST['city']: profile.city = request.POST['city']
        if profile.province != request.POST['province']: profile.province = request.POST['province']
        if profile.state != request.POST['state']: profile.state = request.POST['state']
        if profile.country != request.POST['country']: profile.country = request.POST['country']
        if profile.zip_code != request.POST['zip_code']: profile.zip_code = request.POST['zip_code']
        if applicant.email != request.POST['email']: applicant.email = request.POST['email'] # validate?
        if profile.phone != request.POST['phone']: profile.phone = request.POST['phone']
        profile.save()
        applicant.save()
        messages.info(request, "Profile information updated.")
    # start
    data['applicant'] = applicant
    data['profile'] = profile
    data['application'] = application
    data['form_first_name'] = form_field(applicant.first_name)
    data['form_last_name'] = form_field(applicant.last_name)
    data['form_middle_name'] = form_field(profile.middle_name)
    # <hr/>
    data['form_street1'] = form_field(profile.street1, False, "street1")
    data['form_street2'] = form_field(profile.street2, False, "street2")
    data['form_city'] = form_field(profile.city, False, "city")
    data['form_province'] = form_field(profile.province, False, "province")
    data['form_state'] = form_field(profile.state, False, "state")
    data['form_country'] = form_field(profile.country, False, "country")
    data['form_zip_code'] = form_field(profile.zip_code, False, "zip_code")
    # <hr/>
    data['form_email'] = form_field(applicant.email, False, "email")
    data['form_phone'] = form_field(profile.phone, False, "phone")
    data['form_birthday'] = form_field(profile.birthday)
    data['form_gender'] = form_field(profile.gender)
    data['form_country_birth'] = form_field(profile.country_birth)
    data['form_citizenship'] = form_field(profile.citizenship)
    # <hr/>
    data['form_ref_number'] = form_field(profile.ref_number)
    data['form_date_apply'] = form_field(profile.date_apply)
    # <hr/>
    data['form_enter_qtr'] = form_field(profile.enter_qtr)
    data['form_enter_year'] = form_field(profile.enter_year)
    data['form_degree'] = form_field(profile.degree)
    data['form_major'] = form_field(profile.major)
    # <hr/>
    data['form_gre_taken'] = form_field(profile.gre_taken)
    data['form_o_gre_v'] = form_field(profile.o_gre_v)
    data['form_o_gre_q'] = form_field(profile.o_gre_q)
    data['form_o_gre_a'] = form_field(profile.o_gre_a)
    data['form_o_gre_w'] = form_field(profile.o_gre_w)
    data['form_toefl_taken'] = form_field(profile.toefl_taken)
    data['form_o_toefl_score'] = form_field(profile.o_toefl_score)
    return render_to_response('applicant_templates/profile_info_template.html', data, RequestContext(request))

VALID_CONTENT_TYPES = (
    "application/pdf",
    "image/jpeg",
    "application/msword",
    "application/vnd.openxmlformats-officedocument.wordprocessingml.document",
)

@permission_required('gwaap.is_gwaap_applicant', login_url="/login/")
def uploadResume(request):
    data = dict()
    applicant = Applicant.objects.get(pk=request.user.pk)
    application = applicant.get_application()
    if request.method == "POST":
        if "resume" not in request.FILES:
            messages.error(request, "Error submitting file.")
            return HttpResponseRedirect('/upload_resume/')
        # Verify content type
        if request.FILES['resume'].content_type not in VALID_CONTENT_TYPES:
            messages.error(request, "Resume must be in PDF, DOC, DOCX, or JPG formats.")
            return HttpResponseRedirect('/upload_resume/')
        application.resume = request.FILES['resume']
        application.save()
        applicant.save()
        messages.success(request, "Resume uploaded.")
        return HttpResponseRedirect("/view_application/")
    return render_to_response('applicant_templates/upload_resume_template.html', data, RequestContext(request))

@permission_required('gwaap.is_gwaap_applicant', login_url="/login/")
def uploadLetter(request):
    data = dict()
    applicant = Applicant.objects.get(pk=request.user.pk)
    application = applicant.get_application()
    if request.method == "POST":
        if "letter" not in request.FILES:
            messages.error(request, "Error submitting file.")
            return HttpResponseRedirect('/upload_letter/')
        if request.FILES['letter'].content_type not in VALID_CONTENT_TYPES:
            messages.error(request, "Letter of intent must be in PDF, DOC, DOCX, or JPG formats.")
            return HttpResponseRedirect('/upload_letter/')
        application.letter_of_intent = request.FILES['letter']
        application.save()
        applicant.save()
        messages.success(request, "Letter of intent uploaded.")
        return HttpResponseRedirect('/view_application/')
    return render_to_response('applicant_templates/upload_letter_template.html', data, RequestContext(request))
