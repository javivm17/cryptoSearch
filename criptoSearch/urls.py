"""criptoSearch URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
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
from main import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.index),
    path('charge/', views.charge_index),
    path('search_desc/', views.search_by_desc),
    path('fear_greed/', views.fear_and_greed),
    path('login/', views.ingresar),
    path('logout/', views.cerrar_sesion),
    path('signup/', views.registro),
    path('save/<str:crypto_name>', views.save_crypto),
    path('delete/<str:crypto_name>', views.delete_favorite),
    path('favs/', views.favoritos),
    path('charge_rs/', views.charge_rs),
    path('upcoming_icos/', views.upcoming_icos),
]
