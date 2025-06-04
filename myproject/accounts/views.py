from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse
from .models import Admin
from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from .models import Employee, Admin
from django.views.decorators.http import require_POST
import os
from django.conf import settings
import time
 
from .forms import EmployeeForm
from .models import Employee

from .utils import read_admin_excel
 
 
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

    excel_data = read_admin_excel()

    admin = None

    emp = None
 
    # 🛠️ 1. Handle POST for status update

    if request.method == 'POST':

        new_status = request.POST.get('status')
 
        if is_admin:

            try:

                admin = Admin.objects.get(id=request.session.get('admin_id'))

                admin.status = new_status

                admin.save()

            except Admin.DoesNotExist:

                return redirect('login')

        else:

            try:

                emp = Employee.objects.get(id=request.session.get('employee_id'))

                emp.status = new_status

                emp.save()

            except Employee.DoesNotExist:

                return redirect('login')
 
    # 🧠 2. Render page with updated info

    if is_admin:

        if not admin:

            admin = Admin.objects.get(id=request.session.get('admin_id'))

        form = EmployeeForm()

        employees = Employee.objects.all()
 
        return render(request, 'accounts/home.html', {

            'admin': admin,

            'form': form,

            'admin_status': admin.status,

            'employees': employees,

            'excel_data': excel_data,

        })

    else:

        if not emp:

            emp = Employee.objects.get(id=request.session.get('employee_id'))

        admin_obj = Admin.objects.first()

        employees = Employee.objects.all()
 
        return render(request, 'accounts/home.html', {

            'admin': emp,

            'admin_status': admin_obj.status if admin_obj else 'Unavailable',

            'admin_username': admin_obj.username if admin_obj else '',

            'admin_email': admin_obj.email if admin_obj else '',

            'employees': employees,

            'excel_data': excel_data,

        })

 
 
 
 
 
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
 
from django.views.decorators.http import require_POST
from django.http import JsonResponse
 
@require_POST
def update_status(request):
    status = request.POST.get('status')
    user = None
 
    if request.session.get('is_admin'):
        try:
            user = Admin.objects.get(id=request.session['admin_id'])
        except Admin.DoesNotExist:
            pass
    elif request.session.get('employee_id'):
        try:
            user = Employee.objects.get(id=request.session['employee_id'])
        except Employee.DoesNotExist:
            pass
 
    if user:
        user.status = status
        user.save()
        return JsonResponse({'success': True, 'new_status': status})
 
    return JsonResponse({'success': False}, status=400)
 
 
 
 
from django.shortcuts import render, redirect
from django.contrib import messages
import os
import pandas as pd
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

EXCEL_FILENAME = 'Book.xlsx'
EXCEL_PATH = os.path.join(settings.MEDIA_ROOT, EXCEL_FILENAME)

from django.shortcuts import render, redirect
from django.contrib import messages
import os
import pandas as pd
from django.conf import settings
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile

EXCEL_FILENAME = 'Book.xlsx'
EXCEL_PATH = os.path.join(settings.MEDIA_ROOT, EXCEL_FILENAME)

def show_excel_table(request):
    # Handle Excel file upload
    if request.method == 'POST' and request.FILES.get('excel_file'):
        uploaded_file = request.FILES['excel_file']
        try:
            if default_storage.exists(EXCEL_PATH):
                default_storage.delete(EXCEL_PATH)
            default_storage.save(EXCEL_PATH, ContentFile(uploaded_file.read()))
            messages.success(request, "Excel file uploaded successfully.")
            return redirect('excel_table')
        except Exception as e:
            messages.error(request, f"Upload failed: {e}")
            return redirect('excel_table')

    # Read Excel file
    try:
        df = pd.read_excel(EXCEL_PATH)
    except FileNotFoundError:
        messages.error(request, "Excel file not found. Please upload one.")
        df = pd.DataFrame()
    except Exception as e:
        messages.error(request, f"Error reading Excel file: {e}")
        df = pd.DataFrame()

    # Search filter
    query = request.GET.get('q', '').strip().lower()
    if not df.empty and query:
        df = df[df.apply(lambda row: row.astype(str).str.lower().str.contains(query).any(), axis=1)]

    # Compute duration before dropping timestamp columns
    if all(col in df.columns for col in ["Ticket solved - Timestamp", "Ticket assigned - Timestamp"]):
        try:
            df["Ticket solved - Timestamp"] = pd.to_datetime(df["Ticket solved - Timestamp"], errors='coerce')
            df["Ticket assigned - Timestamp"] = pd.to_datetime(df["Ticket assigned - Timestamp"], errors='coerce')

            df["Duration of the ticket"] = df["Ticket solved - Timestamp"] - df["Ticket assigned - Timestamp"]
            df["Duration of the ticket"] = df["Duration of the ticket"].astype(str).str.replace("NaT", "")
        except Exception as e:
            messages.error(request, f"Could not compute duration: {e}")

    # Drop specified columns
    drop_cols = [
        "Ticket solved - Timestamp",
        "Ticket assigned - Timestamp",
        "Ticket updated - Timestamp",
        "Ticket due - Timestamp",
        "Comment"
    ]
    df.drop(columns=[col for col in drop_cols if col in df.columns], inplace=True)

    # Format date columns and clean up
    if not df.empty:
        for col in df.columns:
            if pd.api.types.is_datetime64_any_dtype(df[col]):
                df[col] = df[col].dt.strftime('%Y-%m-%d %H:%M:%S')
            df[col] = df[col].fillna('')

    headers = df.columns.tolist() if not df.empty else []
    rows = df.fillna('').values.tolist() if not df.empty else []

# Create zipped_rows = list of (header, value) pairs per row
    zipped_rows = [list(zip(headers, row)) for row in rows]

    return render(request, 'accounts/excel_table.html', {
            'headers': headers,
            'zipped_rows': zipped_rows,
            'query': request.GET.get('q', '')
})


 
 
from django.shortcuts import render, redirect
import pandas as pd
from django.contrib import messages
from django.urls import reverse
 
def assign_ticket(request):
    if request.method == 'POST':
        ticket_id = request.POST.get('ticket_number')
        assignee = request.POST.get('assignee')
 
        file_path = os.path.join(settings.BASE_DIR, 'media', 'Book.xlsx')
 
        try:
            df = pd.read_excel(file_path, engine='openpyxl')
            df.columns = df.columns.str.strip()  # Clean headers
 
            if ticket_id not in df['Ticket ID'].astype(str).values:
                messages.error(request, "Ticket not found.")
                return redirect(reverse('excel_table'))
 
            ticket_index = df[df['Ticket ID'].astype(str) == ticket_id].index[0]
 
            df.at[ticket_index, 'Assignee name'] = assignee
            with pd.ExcelWriter(file_path, engine='openpyxl', mode='w') as writer:
                df.to_excel(writer, index=False)
           
            messages.success(request, "Ticket assigned (or reassigned) successfully!")
 
        except Exception as e:
            messages.error(request, f"Error: {e}")
 
        return redirect(reverse('excel_table'))
 
    return render(request, 'accounts/assign_ticket.html')
 




