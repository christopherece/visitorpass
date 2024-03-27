# visitor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('login/', views.login_visitor, name='login_visitor'),
    path('signout/', views.signout_visitor, name='signout_visitor'),
    path('logout/<int:id>/', views.logout, name='logout'),
    path('welcome/', views.welcome, name='welcome'),
]
