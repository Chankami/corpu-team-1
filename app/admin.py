from django.contrib import admin
from .models import User, Login, OTPCode, Application


# Register your models here.
admin.site.register(User)
admin.site.register(Login)
admin.site.register(OTPCode)
admin.site.register(Application)