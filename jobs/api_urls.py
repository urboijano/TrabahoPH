"""URL configuration for Django REST Framework API endpoints"""

from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .api_views import JobViewSet, EmployerViewSet, ApplicationViewSet

# Create router for ViewSets
router = DefaultRouter()
router.register(r'jobs', JobViewSet, basename='api_job')
router.register(r'employers', EmployerViewSet, basename='api_employer')
router.register(r'applications', ApplicationViewSet, basename='api_application')

# API URL patterns
urlpatterns = [
    path('', include(router.urls)),
]
