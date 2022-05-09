from django.urls import path
from .views import HomeView, IPETimeWindowDetailView, ProjectIPEStatsDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path(r'ipe-time-window/<int:pk>/', IPETimeWindowDetailView.as_view(), name='ipe-time-window-detail'),
    path(r'project-stats/<int:pk>/', ProjectIPEStatsDetailView.as_view(), name='project-stats'),
]
