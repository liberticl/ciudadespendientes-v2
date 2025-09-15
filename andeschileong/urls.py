"""
URL configuration for andeschileong project.

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
from django.urls import path, include
# from django.conf.urls import handler404
from ciudadespendientes import views
from django.contrib.auth import views as auth_views
from accounts.views import CustomLoginView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('login/', CustomLoginView.as_view(), name='login'),
    path('logout/',
         auth_views.LogoutView.as_view(template_name='accounts/login.html'),
         name='logout'),
    path('buscar/', views.find, name='buscar'),
    path('mapa/', views.show_data, name='show_data'),
    path('', views.welcome, name='welcome'),
    path('404/', views.error_404, name='error_404'),
    path('403/', views.error_403, name='error_403'),

    # Measuring
    path('api/', include('measuring.urls')),
]


# handler404 =
