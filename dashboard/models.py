from django.db import models
from app.models import User

# Create your models here.

# staff_profile Table creation
class StaffProfile(models.Model):
    FACULTY_CHOICES = (
        ('Permanent', 'Permanent'),
        ('Contract', 'Contract')
    )
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name='staff_profile')
    faculty = models.CharField(max_length=50, choices=FACULTY_CHOICES)

#Job Table creation
class Job(models.Model):
    STATUS_CHOICES = (
        ("0", "pending"),
        ("1", "approved"),
        ("2", "rejected")
    )
    FACULTY_CHOICES = (
        ('Arts', 'Arts'),
        ('Business and Economics', 'Business and Economics'),
        ('Engineering and Information Technology',
         'Engineering and Information Technology'),
        ('Fine Arts and Music', 'Fine Arts and Music'),
        ('Medicine', 'Medicine'),
        ('Dentistry and Health Sciences', 'Dentistry and Health Sciences'),
        ('Science', 'Science'),
        ('Law School', 'Law School')
    )

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='jobs')
    code = models.CharField(max_length=15)
    name = models.CharField(max_length=60)
    description = models.TextField()
    start_date = models.DateField()
    end_date = models.DateField()
    comments = models.TextField()
    status = models.CharField(max_length=1, choices=STATUS_CHOICES)
    faculty = models.CharField(
        max_length=50, choices=FACULTY_CHOICES, null=True)

    def __str__(self):
        return f"{self.code} | {self.name}"