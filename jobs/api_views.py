"""API Views for Django REST Framework"""

from rest_framework import viewsets, status, filters
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, IsAuthenticatedOrReadOnly
from rest_framework.pagination import PageNumberPagination
from django_filters.rest_framework import DjangoFilterBackend
from .models import Job, JobSeeker, Employer, Application
from .serializers import (
    JobSerializer, JobListSerializer, JobDetailSerializer,
    EmployerSerializer, ApplicationSerializer, ApplicationDetailSerializer,
    JobSeekerBasicSerializer
)
import logging

logger = logging.getLogger(__name__)


class JobPagination(PageNumberPagination):
    """Custom pagination for Jobs"""
    page_size = 20
    page_size_query_param = 'page_size'
    max_page_size = 100


class JobViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for browsing jobs.
    
    Provides:
    - GET /api/jobs/ - List all active and approved jobs with pagination
    - GET /api/jobs/{id}/ - Get job details
    - GET /api/jobs/category/ - Filter jobs by category
    - GET /api/jobs/province/ - Filter jobs by province
    """
    
    queryset = Job.objects.filter(is_active=True, is_approved=True)
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter, filters.OrderingFilter]
    filterset_fields = ['category', 'province', 'employer']
    search_fields = ['title', 'description', 'location']
    ordering_fields = ['created_at', 'salary']
    ordering = ['-created_at']
    
    def get_serializer_class(self):
        """Use different serializers for list and detail views"""
        if self.action == 'retrieve':
            return JobDetailSerializer
        return JobListSerializer
    
    @action(detail=False, methods=['GET'])
    def by_province(self, request):
        """Get jobs filtered by province"""
        province = request.query_params.get('province', None)
        if not province:
            return Response(
                {'error': 'province parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        jobs = self.queryset.filter(province=province)
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['GET'])
    def by_category(self, request):
        """Get jobs filtered by category"""
        category = request.query_params.get('category', None)
        if not category:
            return Response(
                {'error': 'category parameter is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        jobs = self.queryset.filter(category=category)
        page = self.paginate_queryset(jobs)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(jobs, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def applications(self, request, pk=None):
        """Get all applications for a specific job"""
        job = self.get_object()
        applications = job.applications.all()
        serializer = ApplicationSerializer(applications, many=True)
        return Response(serializer.data)


class EmployerViewSet(viewsets.ReadOnlyModelViewSet):
    """
    API endpoint for browsing employers.
    
    Provides:
    - GET /api/employers/ - List all employers
    - GET /api/employers/{id}/ - Get employer details
    """
    
    queryset = Employer.objects.all()
    serializer_class = EmployerSerializer
    permission_classes = [IsAuthenticatedOrReadOnly]
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.SearchFilter]
    filterset_fields = ['business_type', 'province']
    search_fields = ['business_name', 'business_description']
    
    @action(detail=True, methods=['GET'])
    def jobs(self, request, pk=None):
        """Get all jobs posted by this employer"""
        employer = self.get_object()
        jobs = employer.jobs.filter(is_active=True)
        serializer = JobListSerializer(jobs, many=True)
        return Response(serializer.data)


class ApplicationViewSet(viewsets.ModelViewSet):
    """
    API endpoint for managing job applications.
    
    Provides:
    - GET /api/applications/ - List user's applications
    - POST /api/applications/ - Create a new application
    - GET /api/applications/{id}/ - Get application details
    - PATCH /api/applications/{id}/ - Update application status (admin only)
    """
    
    permission_classes = [IsAuthenticated]
    serializer_class = ApplicationDetailSerializer
    pagination_class = JobPagination
    filter_backends = [DjangoFilterBackend, filters.OrderingFilter]
    filterset_fields = ['status', 'job__category']
    ordering_fields = ['applied_at']
    ordering = ['-applied_at']
    
    def get_queryset(self):
        """Get applications for the current user"""
        user = self.request.user
        try:
            job_seeker = JobSeeker.objects.get(user=user)
            return Application.objects.filter(job_seeker=job_seeker)
        except JobSeeker.DoesNotExist:
            # If user is not a job seeker, return empty queryset
            return Application.objects.none()
    
    def create(self, request, *args, **kwargs):
        """Create a new application"""
        job_id = request.data.get('job_id')
        if not job_id:
            return Response(
                {'error': 'job_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        try:
            job = Job.objects.get(id=job_id)
            job_seeker = JobSeeker.objects.get(user=request.user)
        except (Job.DoesNotExist, JobSeeker.DoesNotExist):
            return Response(
                {'error': 'Job or profile not found'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        # Check if already applied
        existing = Application.objects.filter(job_seeker=job_seeker, job=job).first()
        if existing:
            return Response(
                {'message': 'You have already applied for this job'},
                status=status.HTTP_409_CONFLICT
            )
        
        # Create application
        application = Application.objects.create(
            job_seeker=job_seeker,
            job=job,
            status='pending'
        )
        logger.info(f"New application created: {job_seeker.user.username} applied for {job.title}")
        
        serializer = self.get_serializer(application)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=False, methods=['GET'])
    def my_applications(self, request):
        """Get all applications by current user"""
        applications = self.get_queryset()
        serializer = self.get_serializer(applications, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['GET'])
    def by_job(self, request, pk=None):
        """Get applications for a specific job (employer only)"""
        try:
            job = Job.objects.get(id=pk)
            # Check if user is the employer
            employer = Employer.objects.get(user=request.user)
            if job.employer != employer:
                return Response(
                    {'error': 'You do not have permission to view these applications'},
                    status=status.HTTP_403_FORBIDDEN
                )
            
            applications = job.applications.all()
            serializer = self.get_serializer(applications, many=True)
            return Response(serializer.data)
        except (Job.DoesNotExist, Employer.DoesNotExist):
            return Response(
                {'error': 'Not found'},
                status=status.HTTP_404_NOT_FOUND
            )
