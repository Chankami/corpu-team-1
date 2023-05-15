from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import random
import os


# Create your models here.

PHONE_REGEX = RegexValidator('^[+]{1}(?:[0-9\\-\\(\\)\\/\\.]\\s?){6, 15}[0-9]{1}$', 'Wrong phone number')

class User(AbstractUser):   
    GENDER_CHOICES = (
        ('Male', 'male'),
        ('Female', 'female'),
        ('Other', 'other')
    )
    USER_TYPES = (
        ("1", "admin"),
        ("2", "staff"),
        ("3", "applicant")
    )
    date_of_birth = models.DateField(blank=True, null=True)
    phone_no = PhoneNumberField(blank=True, null=True)
    gender = models.CharField(max_length=10, choices=GENDER_CHOICES, blank=True, null=True)
    user_type = models.CharField(max_length=1, choices=USER_TYPES)
    address = models.CharField(max_length=255,blank=True, null=True)

class Education(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="education")
    from_date = models.DateField()
    to_date = models.DateField()
    institute = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()

class WorkExperience(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="workexperience")
    from_date = models.DateField()
    to_date = models.DateField()
    institute = models.CharField(max_length=200, blank=True, null=True)
    description = models.TextField()    

class Login(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="logins")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user.username} | {self.created_at}"
    
class OTPCode(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="codes")
    code = models.CharField(max_length=5, blank=True)


    def __str__(self):
        return f"{self.user} | {self.code}"


from dashboard.models import Job
class Application(models.Model):
    TIME_SLOTS = (
        ("0", "Unavailable All Day"),
        ("1", "08.00am-10.00am"),
        ("2", "10.00am-12.00pm"),
        ("3", "01.00pm-03.00pm"),
        ("4", "03.00pm-05.00pm"),
        ("5", "05.00pm-07.00pm")
    )
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="applications")
    resume = models.FileField(upload_to='documents/')
    monday = models.CharField(max_length=50)
    tuesday = models.CharField(max_length=50)
    wednesday = models.CharField(max_length=50)
    thursday = models.CharField(max_length=50)
    friday = models.CharField(max_length=50)
    saturday = models.CharField(max_length=50)
    sunday = models.CharField(max_length=50)
    job = models.OneToOneField(Job, on_delete=models.CASCADE, related_name="applications")
    created_at = models.DateTimeField(auto_now_add=True)
    is_shortlisted = models.BooleanField(null=True)
    is_scheduled = models.BooleanField(null=True)

    @property
    def filename(self):
       return os.path.basename(self.resume.name)