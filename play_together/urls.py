from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views

urlpatterns = [
    # path('accounts/', include('django.contrib.auth.urls')),
    path('login', auth_views.LoginView.as_view(template_name='play_together/login.html')),
    # path('', include('play_together.urls')),
]
