from django.urls import path
from . import views


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('do-login/', views.do_login, name='do_login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),  # <-- add this
]
