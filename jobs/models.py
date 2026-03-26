from django.db import models
from django.contrib.auth.models import User

class JobSeeker(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    mobile = models.CharField(max_length=11)
    province = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    barangay = models.CharField(max_length=100)
    skills = models.TextField(blank=True)
    sms_alerts = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"{self.user.first_name} {self.user.last_name}"

class Employer(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    business_name = models.CharField(max_length=200)
    contact_number = models.CharField(max_length=11)
    business_type = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    barangay = models.CharField(max_length=100)
    business_description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return self.business_name

class Job(models.Model):
    CATEGORY_CHOICES = [
        ('Agriculture', 'Agriculture'),
        ('Tourism', 'Tourism'),
        ('Manufacturing', 'Manufacturing'),
        ('Government', 'Government'),
        ('Healthcare', 'Healthcare'),
        ('Education', 'Education'),
        ('Retail', 'Retail'),
        ('Construction', 'Construction'),
        ('Other', 'Other'),
    ]
    
    title = models.CharField(max_length=200)
    employer = models.ForeignKey(Employer, on_delete=models.CASCADE, related_name='jobs')
    description = models.TextField()
    category = models.CharField(max_length=100, choices=CATEGORY_CHOICES)
    location = models.CharField(max_length=300)
    province = models.CharField(max_length=100)
    municipality = models.CharField(max_length=100)
    barangay = models.CharField(max_length=100)
    salary = models.CharField(max_length=100)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)
    
    def __str__(self):
        return self.title

class Application(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('accepted', 'Accepted'),
        ('rejected', 'Rejected'),
    ]
    
    job_seeker = models.ForeignKey(JobSeeker, on_delete=models.CASCADE, related_name='applications')
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    applied_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ('job_seeker', 'job')
    
    def __str__(self):
        return f"{self.job_seeker} - {self.job}"
