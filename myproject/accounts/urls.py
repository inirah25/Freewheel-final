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
    path('update-status/', views.update_status, name='update_status'),
    path('excel/', views.show_excel_table, name='excel_table'),
    path('assign/', views.assign_ticket, name='assign_ticket'),


    path('edit-excel/', views.edit_excel_table, name='edit_excel_table'),

]
if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
