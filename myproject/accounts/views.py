from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from .models import Admin
from django.http import HttpResponse
from django.views.decorators.cache import never_cache

@never_cache # type: ignore
def login_view(request):
    return render(request, 'accounts/login.html')

def do_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        try:
            admin = Admin.objects.get(username=username)
            if admin.password == password:  # plain text check
                request.session['admin_id'] = admin.id
                return redirect('home')
            else:
                messages.error(request, "Invalid password.")
        except Admin.DoesNotExist:
            messages.error(request, "Admin not found.")
    return redirect('login')

def logout_view(request):
    request.session.flush()  # clear session
    return redirect('login')

def home(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('login')
    try:
        admin = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        return redirect('login')
    return render(request, 'accounts/home.html', {'admin': admin})

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        try:
            admin = Admin.objects.get(username=username)
            token = get_random_string(length=48)
            admin.reset_token = token
            admin.token_created_at = timezone.now()
            admin.save()

            reset_url = request.build_absolute_uri(
                reverse('reset_password', args=[token])
            )

            send_mail(
                subject='Reset Your Password',
                message=f'Click the link to reset your password: {reset_url}',
                from_email='noreply@example.com',
                recipient_list=[admin.email],
            )
            return HttpResponse("success")
        except Admin.DoesNotExist:
            return HttpResponse("user_not_found")

def reset_password(request, token):
    try:
        admin = Admin.objects.get(reset_token=token)
    except Admin.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('password1')

        if not new_password or not confirm_password:
            messages.error(request, "Please fill both password fields.")
            return render(request, 'accounts/reset_password.html', {'token': token})

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/reset_password.html', {'token': token})

        admin.password = new_password  # storing plain text (not secure but per your request)
        admin.reset_token = ''
        admin.token_created_at = None
        admin.save()
        request.session.flush()

        return redirect('login')

    #return render(request, 'accounts/reset_password.html', {'token': token})
    return render(request, 'accounts/reset_password.html', {
        'token': token,
        'password_reset_success': True,
    })
