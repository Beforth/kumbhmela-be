from django.urls import path
from . import views

app_name = 'user'

urlpatterns = [
    path('register/', views.register, name='register'),
    path('login/', views.login, name='login'),
    path('profile/', views.ProfileView.as_view(), name='profile'),
    path('change-password/', views.change_password, name='change_password'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
]

