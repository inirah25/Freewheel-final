from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from .models import Admin
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
import time

from .forms import EmployeeForm
from .models import Employee


@never_cache # type: ignore
def login_view(request):
    return render(request, 'accounts/login.html')

from .models import Admin, Employee  # Make sure Employee is imported

def do_login(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']

        # Try Admin first
        try:
            admin = Admin.objects.get(username=username)
            if admin.password == password:
                request.session['admin_id'] = admin.id
                request.session['is_admin'] = True  # flag
                return redirect('home')
            else:
                messages.error(request, "Invalid password.")
                return redirect('login')
        except Admin.DoesNotExist:
            pass  # Try employee next

        # Try Employee
        try:
            emp = Employee.objects.get(username=username)
            if emp.password == password:
                request.session['employee_id'] = emp.id
                request.session['is_admin'] = False  # flag
                return redirect('home')
            else:
                messages.error(request, "Invalid password.")
        except Employee.DoesNotExist:
            messages.error(request, "User not found.")
    return redirect('login')


def logout_view(request):
    request.session.flush()  # clear session
    return redirect('login')

def home(request):
    is_admin = request.session.get('is_admin')

    if is_admin:
        admin_id = request.session.get('admin_id')
        try:
            admin = Admin.objects.get(id=admin_id)
            from .forms import EmployeeForm
            form = EmployeeForm()
            return render(request, 'accounts/home.html', {'admin': admin, 'form': form})
        except Admin.DoesNotExist:
            return redirect('login')
    else:
        emp_id = request.session.get('employee_id')
        try:
            emp = Employee.objects.get(id=emp_id)
            return render(request, 'accounts/home.html', {'admin': emp})  # reuse admin var for simplicity
        except Employee.DoesNotExist:
            return redirect('login')


from .models import Admin, Employee  # Import both

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        # Try Admin first
        try:
            user = Admin.objects.get(username=username)
            is_admin = True
        except Admin.DoesNotExist:
            # Try Employee
            try:
                user = Employee.objects.get(username=username)
                is_admin = False
            except Employee.DoesNotExist:
                return HttpResponse("user_not_found")

        token = get_random_string(length=48)
        user.reset_token = token
        user.token_created_at = timezone.now()
        user.save()

        reset_url = request.build_absolute_uri(
            reverse('reset_password', args=[token])
        )

        send_mail(
            subject='Reset Your Password',
            message=f'Click the link to reset your password: {reset_url}',
            from_email='noreply@example.com',
            recipient_list=[user.email],
        )
        return HttpResponse("success")


import time
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import Employee  # or your user model

def reset_password(request, token):
    try:
        user = Employee.objects.get(reset_token=token)
    except Employee.DoesNotExist:
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

        user.password = new_password  # Store securely in real app!
        user.reset_token = ''
        user.token_created_at = None
        user.save()

        # Show success animation page first
        response = render(request, 'accounts/reset_password.html', {
            'password_reset_success': True,
            'token': token,
        })

        # Sleep for 1 second to allow user to see success animation
        time.sleep(1)

        # After delay, redirect to login page
        return redirect('login')

    # GET request - show reset form
    return render(request, 'accounts/reset_password.html', {'token': token})






def create_employee(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('login')

    try:
        admin = Admin.objects.get(id=admin_id)
    except Admin.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        form = EmployeeForm(request.POST)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']

            username = email.split('@')[0]
            password = get_random_string(length=10)

            # Save to DB
            Employee.objects.create(
                name=name,
                email=email,
                username=username,
                password=password,  # Storing plain for now
                role=role
            )

            # Send email
            send_mail(
                subject='Your account credentials',
                message=f'Username: {username}\nPassword: {password}',
                from_email='noreply@example.com',
                recipient_list=[email]
            )

            messages.success(request, f"Employee {username} created and emailed.")
            return redirect('home')
    else:
        form = EmployeeForm()

    return render(request, 'accounts/home.html', {'form': form, 'admin': admin})
