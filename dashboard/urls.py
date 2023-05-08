from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_dashboard, name='login_dashboard'),
    path('logout', views.logout_dashboard, name="logout_dashboard"), 
    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset/password_reset_done.html'),name='password_reset_done'),
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='dashboard/password_reset/password_reset_form.html'), name='password_reset'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset/password_reset_complete.html'),
     name='password_reset_complete'),
    
]