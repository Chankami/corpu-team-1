
from django.urls import path
from . import views
urlpatterns = [
    path('', views.index, name="index"),
    path('applicant/login', views.applicant_login, name="applicant_login"),
    path('applicant/register', views.applicant_register, name="applicant_register"),
    path('logout', views.logout_user, name="logout_user"),
    path('applicant/otp', views.otp_view, name="applicant_otp"),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
]