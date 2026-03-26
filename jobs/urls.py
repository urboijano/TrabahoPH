from django.urls import path
from . import views
from . import admin_views
from . import dashboard_views

urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('auth/', views.AuthView.as_view(), name='auth'),
    path('register/', views.RegisterView.as_view(), name='register'),
    path('login/', views.LoginView.as_view(), name='login'),
    path('register-seeker/', views.RegisterJobSeekerView.as_view(), name='register_seeker'),
    path('register-employer/', views.RegisterEmployerView.as_view(), name='register_employer'),
    path('logout/', views.LogoutView.as_view(), name='logout'),
    path('jobs/', views.JobListView.as_view(), name='job_list'),
    path('apply/<int:job_id>/', views.ApplyJobView.as_view(), name='apply_job'),
    
    # Admin Dashboard URLs
    path('admin-dashboard/', admin_views.AdminDashboardView.as_view(), name='admin_dashboard'),
    path('admin-dashboard/jobs/', admin_views.ManageJobsView.as_view(), name='manage_jobs'),
    path('admin-dashboard/applications/', admin_views.ManageApplicationsView.as_view(), name='manage_applications'),
    path('admin-dashboard/users/', admin_views.ManageUsersView.as_view(), name='manage_users'),
    
    # New Dashboard URLs
    path('seeker-dashboard/', dashboard_views.SeekerDashboardView.as_view(), name='seeker_dashboard'),
    path('employer-dashboard/', dashboard_views.EmployerDashboardView.as_view(), name='employer_dashboard'),
]
