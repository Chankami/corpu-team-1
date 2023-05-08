from django.shortcuts import render, redirect
from django.http import HttpResponse, HttpResponseRedirect
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from phonenumber_field.phonenumber import PhoneNumber
import json
from django.contrib.sites.shortcuts import get_current_site
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode
from django.template.loader import render_to_string
from django.utils.encoding import force_str
from django.utils.http import urlsafe_base64_decode
from django.core.mail import send_mail
from django.conf import settings
import random
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
