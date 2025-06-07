from django.urls import path
from . import views
from django.conf.urls.static import static
from django.conf import settings


urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('do-login/', views.do_login, name='do_login'),
    path('forgot-password/', views.forgot_password, name='forgot_password'),
    path('reset-password/<str:token>/', views.reset_password, name='reset_password'),
    path('home/', views.home, name='home'),
    path('logout/', views.logout_view, name='logout'),  # <-- add this
    path('create-employee/', views.create_employee, name='create_employee'),
    path('notice/', views.notice_view, name='notice'),
    path('excel/', views.show_excel_table, name='excel_table'),
    path('assign/', views.assign_ticket, name='assign_ticket'),
    path('user/', views.user, name='user'),
    path('status/', views.status_view, name='status'),
    path('show-shift-mail/', views.submitted_shift_end, name='submitted_shift_end'),
    path('shift-mail/', views.shift_end_email, name='shift_end_email'),
    path('profile/', views.view_profile, name='view_profile'),
    path('upload-profile-image/', views.upload_profile_image, name='upload_profile_image'),


    

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
   
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
