from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from .models import User, Login, OTPCode
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

from django.core.mail import send_mail
from django.conf import settings
import random

# Create your views here.


def index(request):
    if not request.user.is_authenticated:
        return HttpResponseRedirect(reverse('applicant_login'))
        
    return render(request, 'app/main.html')
    

def applicant_login(request):
    if request.method == 'POST':
        try:

            email = request.POST.get("username")
            password = request.POST.get("password")

            print(request.POST)
            
            user = authenticate(username=email, password=password)
            print(user)
            if user is not None:
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
            return HttpResponseRedirect(reverse('index'))
    




    return render(request, 'app/applicant_login.html')


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



def logout_user(request):
    if request.user.is_authenticated:
        logout(request)
        request.session['is_verified'] = False
    return HttpResponseRedirect(reverse('applicant_login'))


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
                return HttpResponseRedirect(reverse('index'))
            
        logout_user(request)
        messages.error(request,  'OTP verification failed!')
        return HttpResponseRedirect(reverse('applicant_login'))
    return render(request, 'app/applicant_otp.html')


def send_confirmation_email(request, user, email):
    current_site = get_current_site(request)
    print("current site", current_site)
    subject = 'Activate your CorpU account'
    message = render_to_string('app/emails/confirmation_email.html', {
        'user': user,
        'domain': current_site.domain,
        'uid': urlsafe_base64_encode(force_bytes(user.pk)),
        'token': account_activation_token.make_token(user),
        'protocol': 'https' if request.is_secure() else 'http'

    })
    # user.email_user(subject, message)
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    messages.success(request, f"Please check your email to confirm your registration")

def send_verification_otp(request, otp_code, user):
    
    subject = 'One Time Password for CorpU'
    message = render_to_string('app/emails/otp_verification_email.html', {
        'user': user,
        'code': otp_code

    })
    # user.email_user(subject, message)
    send_mail(subject, message, settings.EMAIL_HOST_USER, [user.email], fail_silently=False)
    messages.success(request, f"Please check your email for OTP code")


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
        return redirect('applicant_login')
    else:
        messages.warning(request, ('The confirmation link was invalid, possibly because it has already been used.'))
        return redirect('index')