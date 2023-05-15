
from django.urls import path
from . import views
urlpatterns = [
    path('', views.job_list, name="app_index"),
    path('applicant/login', views.applicant_login, name="applicant_login"),
    path('applicant/register', views.applicant_register, name="applicant_register"),
    path('logout', views.logout_user, name="logout_user"),
    path('applicant/otp', views.otp_view, name="applicant_otp"),
    path('profile', views.user_profile, name="user_profile"),
    path('add_education', views.add_education, name="add_education"),
    path('change_password', views.change_password, name="change_password"),
    path('add_work_experience', views.add_work_experience, name="add_work_experience"),
    path('profile', views.user_profile, name="user_profile"),
    path('jobs', views.job_list, name="job_list"),
    path('appliedjobs', views.applied_jobs, name="applied_jobs"),
    path('apply_filter', views.apply_filter, name="apply_filter"),
    path('applicant/activate/<uidb64>/<token>/', views.activate_account, name='activate_applicant'),
]