"""
URL configuration for bc_project project.

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/5.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path

from beautiful_chat import views, profile
from .consumers import ChatConsumer

urlpatterns = [
    path('admin/', admin.site.urls),
    path('chats/', views.chats),
    path('chats/create/', views.new_chat),
    path('chats/<str:chat_id>/', views.chats),
    path('chats/<str:chat_id>/message/', views.incoming_message),
    path('profile_picture/<str:username>', profile.profile_picture),
    path('profile_picture/', profile.profile_picture),
    path('profile/', profile.view_profile),
    path('login/', profile.loginRoute),
    path('logout/', profile.logoutRoute),
    path('register/', profile.register),
    path('', views.index)
]

websocket_urlpatterns = [
    path('ws/chats/<str:chat_id>/', ChatConsumer.as_asgi()),
]
