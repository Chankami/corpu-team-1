from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import User, Login, OTPCode, Education, WorkExperience, Application
from dashboard.models import Job
from django.core.exceptions import ValidationError
from phonenumber_field.phonenumber import PhoneNumber
from django.db.utils import IntegrityError
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from .tokens import account_activation_token

from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.paginator import Paginator
from django.contrib.auth import update_session_auth_hash
from django.core.mail import send_mail
from django.conf import settings
import random

# Create your views here.

#Applicant Login
def applicant_login(request):

    if request.user.is_authenticated and request.user.user_type == '3':
        return HttpResponseRedirect(reverse('app_index'))

    if request.method == 'POST':
        try:

            email = request.POST.get("username")
            password = request.POST.get("password")

            print(request.POST)
            
            user = authenticate(username=email, password=password)
            print(user)
            if user is not None:
                if user.user_type != '3':
                    messages.error(request, 'Only Applicants can login here!')
                    return HttpResponseRedirect(reverse('applicant_login'))
                login(request, user)

                request.session['is_verified'] = False

                number_list = [x for x in range(10)]
                codes = []

                for i in range(5):
                    digit = random.choice(number_list)
                    codes.append(digit)
                
                code = "".join(str(item) for item in codes)
                

                otp_code, created = OTPCode.objects.update_or_create(
                    user=user,
                    defaults={"code": code},
                )
                print(otp_code)
                print(otp_code.code)

                send_verification_otp(request, otp_code.code, user)
                return HttpResponseRedirect(reverse('applicant_otp'))
                
            else:
                messages.add_message(request, messages.ERROR, 'Email or password incorrect')
                return HttpResponseRedirect(reverse('applicant_login'))
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect(reverse('app_index'))

    return render(request, 'app/applicant_login.html')


# Applicant Registration
def applicant_register(request):
    if request.method == 'POST':
        fname = request.POST['firstname']
        lname = request.POST['lastname']
        email = request.POST['emailaddress']
        phone_no = request.POST['phoneno']
        password = request.POST['password']
        cpassword = request.POST['confirm-password']
        dob = request.POST['dob']
        gender = request.POST['gender']
        address = request.POST['address']

        print(request.POST)

        if password != cpassword:
            print("passwords do not match")
            messages.error(request,  "passwords do not match")
            return HttpResponseRedirect(reverse("applicant_register"))

        number = PhoneNumber.from_string(phone_no, region="AU")
        print(number.as_national)
        print(number.as_e164)

        try:
             new_user = User.objects.create_user(first_name = fname, last_name=lname, username=email, email = email, phone_no = number.as_e164, password=password, date_of_birth = dob, gender=gender, address=address, user_type="3")   
             new_user.is_active = False
             new_user.save()
             send_confirmation_email(request, new_user, email)
             return HttpResponseRedirect(reverse('applicant_register'))
        except ValidationError as e:
            print(str(e))
            pass
            messages.error(request,  str(e))
            return HttpResponseRedirect(reverse('applicant_register'))
        except IntegrityError as e:
            messages.error(request,  "User with this email already exists!")
            print(str(e))
            return HttpResponseRedirect(reverse('applicant_register'))

    return render(request, 'app/applicant_register.html')

#Logout Applicant
def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        request.session['is_verified'] = False
    return HttpResponseRedirect(reverse('applicant_login'))

#OTP for Applicant
def otp_view(request):

    if not request.user.is_authenticated:
        return redirect('applicant_login')
    
    if request.method == 'POST':
        code = request.POST['otp']
        print(code)
        otp_codes = OTPCode.objects.filter(user=request.user)
        print(otp_codes)
        if otp_codes:
            if otp_codes[0].code == code:
                new_login = Login(user=request.user)
                new_login.save()
                request.session['is_verified'] = True
                messages.success(request,  'Logged in!')
                return HttpResponseRedirect(reverse('app_index'))
            
        logout_user(request)
        messages.error(request,  'OTP verification failed!')
        return HttpResponseRedirect(reverse('applicant_login'))
    return render(request, 'app/applicant_otp.html')

#Applicant confirmation_email 
def send_confirmation_email(request, user, email):
    current_site = get_current_site(request)
    print("current site", current_site)
    subject = 'Confirm your account'
    message = render_to_string('app/emails/confirmation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'

    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    messages.success(request, f"Please check your email to confirm your registration")

#Send otp email
def send_verification_otp(request, otp_code, user):

    subject = 'One Time Password for CorpU'
    message = render_to_string('app/emails/otp_verification_email.html', {
        'user': user,
        'code': otp_code
    })
    send_mail(subject, message, settings.EMAIL_HOST_USER,
              [user.email], fail_silently=False)
    messages.success(request, f"Please check your email for OTP code")

#Applicant account activation
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        
        user.save()
        messages.success(request, ('Your account have been verified. You can login now'))
        return redirect('applicant_login')
    else:
        messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('app_index')

#User profile details applicant
def user_profile(request):

    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse(applicant_login))
    if request.method == 'POST':
        phone_no = request.POST['phone_no']
        number = PhoneNumber.from_string(phone_no, region="AU")
        print(number.as_national)
        print(number.as_e164)
        request.user.phone_no = number.as_e164
        request.user.save()
        messages.success(request, 'Profile Updated')
        return HttpResponseRedirect(reverse('user_profile'))
    education_history = Education.objects.filter(user=request.user).order_by('from_date')
    work_history = WorkExperience.objects.filter(user=request.user).order_by('from_date')

    print(education_history)
    print(work_history)
    return render(request, 'app/profile.html', {'education': education_history, 'work': work_history})

#Add education details
def add_education(request):

    if request.method == 'POST':
        to_date = request.POST['to_date']
        from_date = request.POST['from_date']
        institute = request.POST['institute']
        desc = request.POST['description']

        edu = Education(to_date=to_date, from_date=from_date, institute=institute, description=desc, user=request.user)
        edu.save()

        return HttpResponseRedirect(reverse('user_profile'))        
    pass

#Add work details
def add_work_experience(request):
     if request.method == 'POST':
        to_date = request.POST['to_date']
        from_date = request.POST['from_date']
        institute = request.POST['institute']
        desc = request.POST['description']

        work = WorkExperience(to_date=to_date, from_date=from_date, institute=institute, description=desc, user=request.user)
        work.save()

        return HttpResponseRedirect(reverse('user_profile')) 

#Change password 
def change_password(request):
    if request.method == 'POST':
        password = request.POST['password']
        password_con = request.POST['password-con']

        if password != password_con:
            messages.error(request, "Passwords do not match")
            return HttpResponseRedirect(reverse('user_profile'))
        
        try:
            request.user.set_password(password)
            request.user.save()
            update_session_auth_hash(request, request.user)
            messages.success(request, "Password changed")
            return HttpResponseRedirect(reverse('user_profile'))

        except Exception as e:
            print(str(e))
            messages.error(request, "Error changing password")
            return HttpResponseRedirect(reverse('user_profile'))

#Job list
from django.db.models import Q
from django.utils.http import urlencode

#Job list
def job_list(request):
    if not request.user.is_authenticated or request.user.user_type != '3' :
        return HttpResponseRedirect(reverse('applicant_login'))

    if request.method == 'POST' and request.FILES['resume']:

        print(request.POST)
        monday = ['0']
        tuesday = ['0']
        wednesday = ['0']
        thursday = ['0']
        friday = ['0']
        saturday = ['0']
        sunday = ['0']

        if 'monday' in request.POST:
            monday = request.POST.getlist('monday')
        if 'tuesday' in request.POST:
            tuesday = request.POST.getlist('tuesday')
        if 'wednesday' in request.POST:
            wednesday = request.POST.getlist('wednesday')
        if ' thursday' in request.POST:
            thursday = request.POST.getlist('thursday')
        if 'friday' in request.POST:
            friday = request.POST.getlist('friday')
        if 'saturday' in request.POST:
            saturday = request.POST.getlist('saturday')
        if 'sunday' in request.POST:
            sunday = request.POST.getlist('sunday')
        job_id = request.POST['job_id']

        print(monday)

        myfile = request.FILES['resume']
        
        job = Job.objects.filter(id=job_id).first()

        try:
            new_app = Application(user=request.user, job=job, monday=monday, tuesday=tuesday, wednesday=wednesday, thursday=thursday, friday=friday, saturday=saturday, sunday=sunday, resume=myfile)
            new_app.save()
            send_applied_to_job_email(request, request.user, job.code, job.name)
            
        except IntegrityError as e:
            messages.error(request, "You have already applied to this job!")
            return HttpResponseRedirect(reverse('job_list'))
        messages.success(request, "Application saved")
        return HttpResponseRedirect(reverse('job_list'))
    
    if 'filters' in request.GET:
       filters = request.GET.get("filters")
       print(filters)

       filter_list = filters.replace('%20', ' ').split(',')
       
       jobs = Job.objects.filter(faculty__in=filter_list, status='1')
    else:
       jobs = Job.objects.filter(status='1').order_by('-id') 
    print("JOBS")
    print(jobs)
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    my_applications = Application.objects.filter(user=request.user)
    job_list = []
    for app in my_applications:
        job_list.append(app.job.id)
    print(page_obj)
    print(job_list)

    filter_count = {}
    filter_count["all"] = Job.objects.filter(status='1').count()
    filter_count["arts"] = Job.objects.filter(faculty='Arts', status='1').count()
    filter_count["business"] = Job.objects.filter(faculty='Business and Economics', status='1').count()
    filter_count["engineering"] = Job.objects.filter(faculty='Engineering and Information Technology', status='1').count()
    filter_count["finearts"] = Job.objects.filter(faculty='Fine Arts and Music', status='1').count()
    filter_count["medicine"] = Job.objects.filter(faculty='Medicine', status='1').count()
    filter_count["dentistry"] = Job.objects.filter(faculty='Dentistry and Health Sciences', status='1').count()
    filter_count["science"] = Job.objects.filter(faculty='Science', status='1').count()
    filter_count["law"] = Job.objects.filter(faculty='Law School', status='1').count()
    return render(request, 'app/job_list.html', {"page_obj": page_obj, "applied_jobs": job_list, 'filter_count': filter_count}) 

#filter jobs
def apply_filter(request):
    if request.method == 'POST':
        filters = []
        print(request.POST)
        for key in request.POST:
            if key != 'csrfmiddlewaretoken':
                filters.append(key)

        return HttpResponseRedirect(reverse('job_list') + f'?filters={",".join(filters)}')
    return HttpResponseRedirect(reverse('job_list'))

#Apply Job
def applied_jobs(request):
    
    my_applications = Application.objects.filter(user=request.user)
    job_list = []
    for app in my_applications:
        job_list.append({
            "job": app.job,
            "is_scheduled": app.is_scheduled
        })
 
    print(job_list)
    return render(request, 'app/applied_jobs.html', {"jobs": job_list})

#Send email to applicant once job apply
def send_applied_to_job_email(request, user, unit_code, unit_name):
    
    subject = 'Thanks For Applying With CorpU'
    message = render_to_string('app/emails/applied_to_job_email.html', {
        'firstname': user.first_name,
        'lastname': user.last_name,
        'unit_code': unit_code,
        'unit_name': unit_name 

    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)




















