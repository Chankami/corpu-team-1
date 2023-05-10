from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from phonenumber_field.phonenumber import PhoneNumber
import json
from app.models import User, OTPCode
from .models import StaffProfile, Job
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from app.tokens import account_activation_token
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
import random
import datetime
from django.db.utils import IntegrityError
from django.core.paginator import Paginator

# Create your views here.

def index(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Please login first')
        return HttpResponseRedirect(reverse('login_dashboard'))
    return render(request, 'dashboard/index.html')

 #Login of Staff/admin dashboard  
def login_dashboard(request):
    if request.method == 'POST':
        try:
            email = request.POST.get("email")
            password = request.POST.get("password")
            print(request.POST)
            user = authenticate(username=email, password=password)
            print(user)
            if user is not None:
                if user.user_type == '3':
                    messages.error(request, 'Not authorized to login')
                    return HttpResponseRedirect(reverse('login_dashboard'))
                if user.user_type == '2':
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
                    return HttpResponseRedirect(reverse('staff_otp'))

                login(request, user)
                return HttpResponseRedirect(reverse('index'))
                
            else:
                messages.add_message(request, messages.ERROR, 'Email or password incorrect')
                return HttpResponseRedirect(reverse('login_dashboard'))
        except Exception as e:
            print(str(e))
            return HttpResponseRedirect(reverse('index'))
    return render(request, 'dashboard/login.html')

 #Logout Staff/admin dashboard   
def logout_dashboard(request):
    if request.user.is_authenticated:
        logout(request)
        
    return HttpResponseRedirect(reverse('login_dashboard'))

#Send reset email for staff
def send_reset_link(request,email):
    from django.http import HttpRequest
    from django.contrib.auth.forms import PasswordResetForm
    try:  
        form = PasswordResetForm({'email': email})
        if form.is_valid():
            print("Sending email for to this email:", email)
            form.save(request=request, from_email=settings.EMAIL_HOST_USER, 
                email_template_name='dashboard/password_reset/password_reset_email.html')

    except Exception as e:
        print(str(e))
    return 'success'

#Send OTP for staff
def send_verification_otp(request, otp_code, user):
    
    subject = 'One time Password - CorpU'
    message = render_to_string('app/emails/otp_verification_email.html', {
        'user': user,
        'code': otp_code

    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    messages.success(request, f"Please check your email for OTP code")

#Send account confirmation for staff
def send_confirmation_email(request, user, email):
    current_site = get_current_site(request)
    print("current site", current_site)
    subject = 'Confirm your CorpU account'
    message = render_to_string('dashboard/emails/confirmation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'

    })
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    messages.success(request, f"Please check your email to confirm your registration")

#OTP implementation
def otp_view(request):
    if not request.user.is_authenticated:
        return redirect('login_dashboard')
    if request.method == 'POST':
        code = request.POST['otp']
        print(code)
        otp_codes = OTPCode.objects.filter(user=request.user)
        print(otp_codes)
        if otp_codes:
            if otp_codes[0].code == code:
                
                request.session['is_verified'] = True
                messages.success(request,  'Logged in!')
                return HttpResponseRedirect(reverse('index'))    
        logout_dashboard(request)
        messages.error(request,  'OTP verification failed!')
        return HttpResponseRedirect(reverse('login_dashboard'))
    return render(request, 'dashboard/staff_otp.html')

#Account activaion
def activate_account(request, uidb64, token):
    try:
        uid = force_str(urlsafe_base64_decode(uidb64))
        user = User.objects.get(pk=uid)
    except (TypeError, ValueError, OverflowError, User.DoesNotExist):
        user = None

    if user is not None and account_activation_token.check_token(user, token):
        user.is_active = True
        
        user.save()
        # login(request, user)
        messages.success(request, ('Your account have been verified. You can login now'))
        return redirect('login_dashboard')
    else:
        messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('index')


 #Add Staff by Admin
def add_staff(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Only admins are allowed here')
        return HttpResponseRedirect(reverse('index'))
    
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        phone_no = request.POST['phone_no']
        faculty = request.POST['faculty']
        password = request.POST['password']

        number = PhoneNumber.from_string(phone_no, region="AU")
        print(number.as_national)
        print(number.as_e164)

#Edit Staff details
def edit_staff(request, staff_id):
    staff_profile = StaffProfile.objects.filter(id=staff_id).first()
    if request.method == 'POST':
        first_name = request.POST['firstname']
        last_name = request.POST['lastname']
        email = request.POST['email']
        phone_no = request.POST['phone_no']
        faculty = request.POST['faculty']
        try:
        
            user = User.objects.filter(id=staff_profile.user.id).first()
            user.first_name = first_name
            user.last_name = last_name
            user.email = email
            user.phone_no = phone_no
            user.save()
            staff_profile.faculty = faculty
            staff_profile.save()
            messages.success(request, 'Staff updated')
            return HttpResponseRedirect(reverse('manage_staff'))
        except Exception as e:
            print(str(e))
            messages.error(request, 'Staff could be updated')
            return HttpResponseRedirect(reverse('manage_staff')) 
    return render(request, 'dashboard/edit_staff.html', {"profile": staff_profile})

#Manage Staff details
def manage_staff(request):
     if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Only admins are allowed here')
        return HttpResponseRedirect(reverse('index'))
     
     profiles = StaffProfile.objects.all().order_by("id")
     paginator = Paginator(profiles, 10)
     page_number = request.GET.get("page")
     page_obj = paginator.get_page(page_number)

     print(page_obj)
     return render(request, 'dashboard/manage_staff.html', {"page_obj": page_obj})

#Manage Staff details
def delete_staff(request, staff_id):
    staff_profile = StaffProfile.objects.filter(id=staff_id).first()
    if staff_profile:
        user = User.objects.filter(id=staff_profile.user.id).first()
        user.delete()
        staff_profile.delete()
        messages.success(request, 'Staff deleted')
        return HttpResponseRedirect(reverse('manage_staff'))
    messages.error(request, 'Staff profile not found')
    return HttpResponseRedirect(reverse('manage_staff'))

#Add Jobs by Staff     
def add_job(request):
    if not request.user.is_authenticated:
        messages.error(request, 'Log in first')
        return HttpResponseRedirect(reverse('login_dashboard'))
    if request.method == 'POST':
        code = request.POST['code']
        name = request.POST['name']
        description = request.POST['description']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        comments =request.POST['comments']
        faculty = request.POST['faculty']
   
        job = Job(code=code, name=name, description=description, start_date=start_date, end_date=end_date, comments=comments, user=request.user, status="0", faculty=faculty)
        job.save()

        messages.success(request, 'Job added!')
        return HttpResponseRedirect(reverse('add_job'))

    return render(request, 'dashboard/add_job.html', {"current_date": datetime.datetime.today})

#Edit Job
def edit_job(request, job_id):
    job = Job.objects.filter(id=job_id).first()

    if request.method == 'POST':
        code = request.POST['code']
        name = request.POST['name']
        description = request.POST['description']
        start_date = request.POST['start_date']
        end_date = request.POST['end_date']
        comments =request.POST['comments']
        faculty = request.POST['faculty']

        job.code = code
        job.name = name
        job.description = description
        job.start_date = start_date
        job.end_date = end_date
        job.comments = comments
        job.faculty = faculty

        job.save()
        messages.success(request, "Unit updated!")
        return HttpResponseRedirect(reverse('unit_list'))
    if job:
        return render(request, 'dashboard/edit_job.html', {"job": job})
    else:
        messages.error(request, "No unit found")
        return HttpResponseRedirect(reverse('unit_list'))

#List of jobs
def unit_list(request):
    jobs = Job.objects.filter(user=request.user).order_by("id")
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    print(page_obj)
    return render(request, 'dashboard/unit_list.html', {"page_obj": page_obj})  
 
#Delete jobs
def delete_unit(request, job_id):
    if not request.user.is_authenticated:
        messages.error(request, 'Invalid Operation')
        return HttpResponseRedirect(reverse('index'))
    job = Job.objects.filter(id=job_id).first()
    print(job)
    if job:
        print(job.status)
        if job.status == '1':
            job.status = '2'
            job.save()
            messages.success(request, "Job inactive")
            print(job.status)
            if request.user.is_superuser:
                return HttpResponseRedirect(reverse('review_units'))
            else:
               return HttpResponseRedirect(reverse('unit_list')) 
    
    if request.user.is_superuser:
        return HttpResponseRedirect(reverse('review_units'))
    else:
        return HttpResponseRedirect(reverse('unit_list'))  

 #Review units  
def review_units(request):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Only admins are allowed here')
        return HttpResponseRedirect(reverse('index'))
     
    jobs = Job.objects.all().order_by("id")
    paginator = Paginator(jobs, 10)
    page_number = request.GET.get("page")
    page_obj = paginator.get_page(page_number)

    print(page_obj)
    return render(request, 'dashboard/review_units.html', {"page_obj": page_obj, "current_date": datetime.date.today()})
    
 #Approve Units  
def approve_unit(request, job_id):
    if not request.user.is_authenticated or not request.user.is_superuser:
        messages.error(request, 'Invalid Operation')
        return HttpResponseRedirect(reverse('index'))
    
    job = Job.objects.filter(id=job_id).first()
    if job.status == '1':
        messages.success(request, "Unit is already active!")
        return HttpResponseRedirect(reverse('review_units'))
    job.status = '1'
    job.save()
    messages.success(request, "Unit approved!")
    return HttpResponseRedirect(reverse('review_units'))

    


