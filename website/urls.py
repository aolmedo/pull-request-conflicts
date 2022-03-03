from django.urls import path
from .views import HomeView, IPETimeWindowDetailView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path(r'ipe-time-window/<int:pk>/', IPETimeWindowDetailView.as_view(), name='ipe-time-window-detail'),
]
