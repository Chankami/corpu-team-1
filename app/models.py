from django.db import models
from django.contrib.auth.models import AbstractUser
from phonenumber_field.modelfields import PhoneNumberField
from django.core.exceptions import ValidationError
from django.core.validators import RegexValidator
import random
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
    # def save(self, *args, **kwargs):
    #     number_list = [x for x in range(10)]
    #     codes = []

    #     for i in range(5):
    #         digit = random.choice(number_list)
    #         codes.append(digit)
        
    #     code = "".join(str(item) for item in codes)
    #     self.number = code
    #     print(self.number)

    #     super().save(*args, **kwargs)

