from django.urls import path
from . import views
from django.contrib.auth import views as auth_views

urlpatterns = [
    path('', views.index, name="index"),
    path('login', views.login_dashboard, name='login_dashboard'),
    path('logout', views.logout_dashboard, name="logout_dashboard"), 
    path('reset/<uidb64>/<token>/', auth_views.PasswordResetConfirmView.as_view(template_name='dashboard/password_reset/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/', auth_views.PasswordResetView.as_view(template_name='dashboard/password_reset/password_reset_form.html'), name='password_reset'),
    path('reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset/password_reset_complete.html'),name='password_reset_complete'),
    path('password_change/done/', auth_views.PasswordChangeDoneView.as_view(template_name='dashboard/password_reset/password_change_done.html'),name='password_change_done'),
    path('password_change/', auth_views.PasswordChangeView.as_view(template_name='dashboard/password_reset/password_change.html'),name='password_change'),
    path('password_reset/done/', auth_views.PasswordResetCompleteView.as_view(template_name='dashboard/password_reset/password_reset_done.html'),name='password_reset_done'),
    path('staff/add', views.add_staff, name="add_staff"),
    path('staff/otp', views.otp_view, name="staff_otp"),
    path('staff/manage', views.manage_staff, name="manage_staff"),
    path('staff/edit/<str:staff_id>', views.edit_staff, name="edit_staff"),
    path('staff/delete/<str:staff_id>', views.delete_staff, name="delete_staff"),
    path('jobs/add', views.add_job, name="add_job"),
    path('job/edit/<str:job_id>', views.edit_job, name="edit_job"),
    path('jobs', views.unit_list, name="unit_list"),
    path('jobs/delete/<str:job_id>', views.delete_unit, name="delete_unit"),
    path('jobs/review', views.review_units, name="review_units"),
    path('jobs/approve/<str:job_id>', views.approve_unit, name="approve_unit"),
    path('dashboard/activate/<uidb64>/<token>/', views.activate_account, name='activate_dashboard'),

    path('candidates', views.manage_candidates, name="manage_candidates"),
    path('approve_application/<str:app_id>', views.approve_application, name="approve_application"),
    path('reject_application/<str:app_id>', views.reject_application, name="reject_application"),
     
    path('schedule', views.schedule, name='schedule'),
    path('schedule/approve/<str:app_id>', views.schedule_application, name="schedule_application"),
    path('schedule/reject/<str:app_id>', views.reject_schedule, name="reject_schedule"),
    path('detail_schedule', views.detail_schedule, name='detail_schedule'),

    
]