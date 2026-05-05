"""Serializers for Django REST Framework API"""

from rest_framework import serializers
from .models import Job, JobSeeker, Employer, Application


class EmployerSerializer(serializers.ModelSerializer):
    """Serializer for Employer model"""
    
    business_email = serializers.CharField(source='user.email', read_only=True)
    full_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Employer
        fields = [
            'id',
            'business_name',
            'business_type',
            'business_description',
            'contact_number',
            'province',
            'municipality',
            'barangay',
            'business_email',
            'full_name',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_full_name(self, obj):
        """Get employer contact person full name"""
        user = obj.user
        return f"{user.first_name} {user.last_name}"


class JobSerializer(serializers.ModelSerializer):
    """Serializer for Job model"""
    
    employer_name = serializers.CharField(source='employer.business_name', read_only=True)
    employer_business_type = serializers.CharField(source='employer.business_type', read_only=True)
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'employer',
            'employer_name',
            'employer_business_type',
            'description',
            'category',
            'location',
            'province',
            'municipality',
            'barangay',
            'salary',
            'is_active',
            'applications_count',
            'created_at',
            'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']
    
    def get_applications_count(self, obj):
        """Get total number of applications for this job"""
        return obj.applications.count()


class JobDetailSerializer(JobSerializer):
    """Detailed serializer for Job model with employer info"""
    
    employer = EmployerSerializer(read_only=True)


class JobListSerializer(serializers.ModelSerializer):
    """Simplified serializer for job list view"""
    
    employer_name = serializers.CharField(source='employer.business_name', read_only=True)
    applications_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Job
        fields = [
            'id',
            'title',
            'employer_name',
            'category',
            'location',
            'province',
            'salary',
            'applications_count',
            'created_at'
        ]
    
    def get_applications_count(self, obj):
        """Get total number of applications for this job"""
        return obj.applications.count()


class JobSeekerBasicSerializer(serializers.ModelSerializer):
    """Serializer for JobSeeker model (basic info only)"""
    
    full_name = serializers.SerializerMethodField()
    email = serializers.CharField(source='user.email', read_only=True)
    
    class Meta:
        model = JobSeeker
        fields = [
            'id',
            'full_name',
            'email',
            'mobile',
            'province',
            'municipality',
            'barangay',
            'skills',
            'created_at'
        ]
        read_only_fields = ['id', 'created_at']
    
    def get_full_name(self, obj):
        """Get job seeker full name"""
        user = obj.user
        return f"{user.first_name} {user.last_name}"


class ApplicationSerializer(serializers.ModelSerializer):
    """Serializer for Application model"""
    
    job_seeker_name = serializers.CharField(source='job_seeker.user.get_full_name', read_only=True)
    job_title = serializers.CharField(source='job.title', read_only=True)
    employer_name = serializers.CharField(source='job.employer.business_name', read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)
    
    class Meta:
        model = Application
        fields = [
            'id',
            'job_seeker',
            'job_seeker_name',
            'job',
            'job_title',
            'employer_name',
            'status',
            'status_display',
            'applied_at'
        ]
        read_only_fields = ['id', 'applied_at']


class ApplicationDetailSerializer(ApplicationSerializer):
    """Detailed serializer for Application with more information"""
    
    job_seeker = JobSeekerBasicSerializer(read_only=True)
    job = JobDetailSerializer(read_only=True)
