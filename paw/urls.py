"""paw URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
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
from django.urls import include, path
from core import views as core

urlpatterns = [
    path('', core.index, name='home'),
    path('admin/', admin.site.urls),
    path('console/', include('console.urls')),
    path('merchants/', include('merchants.urls')),
    path('panels/', include('panels.urls')),
    path('performers/', include('performers.urls')),
    path('volunteers/', include('volunteers.urls')),
    path('partyfloor/', include('partyfloor.urls')),
    path('dancecomp/', include('dancecomp.urls'))
]
