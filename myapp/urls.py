from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('upload/', views.VisitorManagementSystem.upload_image, name='upload_image'),
    path('capture/', views.VisitorManagementSystem.capture_image, name='capture_image'),
]