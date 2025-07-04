# visitor/urls.py
from django.urls import path
from . import views

urlpatterns = [
    path('', views.login_visitor, name='login'),  # Make login the default page
    path('signout/', views.signout_visitor, name='signout_visitor'),
    path('logout/<int:id>/', views.logout, name='logout'),
    path('welcome/', views.welcome, name='welcome'),
    path('search-staff/', views.search_staff, name='search_staff'),
]
