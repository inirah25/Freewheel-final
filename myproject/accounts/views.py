from django.shortcuts import render, redirect
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse

from django.http import HttpResponse
from django.views.decorators.cache import never_cache
from .models import User, Notice
from django.views.decorators.http import require_POST
import os
from django.conf import settings
import time
 
from .forms import EmployeeForm


from .utils import read_admin_excel
 
 
@never_cache # type: ignore
def login_view(request):
    return render(request, 'accounts/login.html')
 
from .models import User  # Make sure Employee is imported
 
def do_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        try:
            user = User.objects.get(username=username)
            if user.password == password:  # still plaintext
                # Store admin session key correctly
                if user.access == 'admin':
                    request.session['admin_id'] = user.id
                else:
                    request.session['user_id'] = user.id
                return redirect('home')
            else:
                messages.error(request, "Invalid password.")
        except User.DoesNotExist:
            messages.error(request, "User not found.")

    return redirect('login')

 
 
def logout_view(request):
    request.session.flush()  # clear session
    return redirect('login')
 
 
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User, Notice

from .forms import EmployeeForm
from .utils import read_admin_excel  # assuming you have this util function

def home(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    access = user.access  # 'admin', 'staff', or 'guest'

    all_notices = Notice.objects.order_by('-posted_at')
    users = User.objects.all().values(
    'name', 'role', 'shift', 'status', 'email', 'reporting_manager',
    'teams_chat_link', 'profile_image'
)
    excel_data = read_admin_excel()  # Make sure this function returns valid data

    if request.method == 'POST':
        # Posting a notice
        if 'notice_message' in request.POST:
            message = request.POST.get('notice_message')
            if message.strip():
                Notice.objects.create(message=message, posted_by=user.name)
                messages.success(request, "Notice posted successfully.")
            else:
                messages.error(request, "Notice message cannot be empty.")
            return redirect('home')

        # Deleting a notice
        elif 'delete_notice_id' in request.POST:
            notice_id = request.POST.get('delete_notice_id')
            try:
                notice = Notice.objects.get(id=notice_id)
                # Only allow deletion if posted by the same user or if admin
                if notice.posted_by == user.name or access == 'admin':
                    notice.delete()
                    messages.success(request, "Notice deleted successfully.")
                else:
                    messages.error(request, "You can only delete your own notices.")
            except Notice.DoesNotExist:
                messages.error(request, "Notice not found.")
            return redirect('home')

        # Updating user status
        elif 'status' in request.POST:
            new_status = request.POST.get('status')
            if new_status in dict(User._meta.get_field('status').choices):
                user.status = new_status
                user.save()
                messages.success(request, "Status updated successfully.")
            else:
                messages.error(request, "Invalid status value.")
            return redirect('home')

    context = {
        'user': user,
        'access': access,
        'users': users,
        'excel_data': excel_data,
        'notices': all_notices,
        'MEDIA_URL': settings.MEDIA_URL,
    }

    if access == 'admin':
        context['form'] = EmployeeForm()

    return render(request, 'accounts/home.html', context)


from django.shortcuts import render, redirect
from django.views.decorators.cache import never_cache
from django.contrib import messages

@never_cache
def user(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')

    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')

    # Only allow admin or staff to view users list
    if user.access not in ['admin', 'staff']:
        messages.error(request, "You do not have permission to view users.")
        return redirect('home')

    # Define shift display mapping
    SHIFT_NAMES = {
        'shift1': 'S1',
        'shift2': 'S2',
        'shift3': 'S3',
    }

    # Fetch all users without select_related (if reporting_manager is not FK)
    users_qs = User.objects.all()

    users = []
    for u in users_qs:
        # Get shift display or fallback to raw shift
        shift_display = SHIFT_NAMES.get(u.shift, u.shift)

        # If reporting_manager is a ForeignKey to User or another model:
        # Replace the next line with u.reporting_manager.name if it is a FK
        reporting_manager_name = u.reporting_manager if isinstance(u.reporting_manager, str) else (u.reporting_manager.name if u.reporting_manager else '')

        users.append({
            'name': u.name,
            'email': u.email,
            'role': u.role,
            'status': u.status,
            'shift': shift_display,
            'reporting_manager': reporting_manager_name,
            'profile_image': u.profile_image.url if u.profile_image else '',
            'teams_chat_link': u.teams_chat_link,
        })

    return render(request, 'accounts/user.html', {'users': users, 'user':user})

 
 
from django.http import HttpResponse
from django.utils.crypto import get_random_string
from django.utils import timezone
from django.core.mail import send_mail
from django.urls import reverse

def forgot_password(request):
    if request.method == 'POST':
        username = request.POST.get('username')

        try:
            user = User.objects.get(username=username)
        except User.DoesNotExist:
            return HttpResponse("user_not_found")

        # Optionally: You can check access here if you want to restrict certain users
        # For example:
        # if user.access not in ['admin', 'staff', 'guest']:
        #     return HttpResponse("user_not_found")

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
from .models import User  # unified User model

def reset_password(request, token):
    try:
        user = User.objects.get(reset_token=token)
    except User.DoesNotExist:
        messages.error(request, "Invalid or expired reset link.")
        return redirect('login')

    # Optional: you can check token expiration if you track token_created_at

    if request.method == 'POST':
        new_password = request.POST.get('password')
        confirm_password = request.POST.get('password1')

        if not new_password or not confirm_password:
            messages.error(request, "Please fill both password fields.")
            return render(request, 'accounts/reset_password.html', {'token': token})

        if new_password != confirm_password:
            messages.error(request, "Passwords do not match.")
            return render(request, 'accounts/reset_password.html', {'token': token})

        # Store password securely (use hashing in real app)
        user.password = new_password  
        user.reset_token = ''
        user.token_created_at = None
        user.save()

        # Show success animation page first
        response = render(request, 'accounts/reset_password.html', {
            'password_reset_success': True,
            'token': token,
        })

        time.sleep(1)  # Give time to see success animation

        return redirect('login')

    # GET request - show reset form
    return render(request, 'accounts/reset_password.html', {'token': token})

 
 
 
 
from django.contrib import messages
from django.utils.crypto import get_random_string
from django.core.mail import send_mail
from django.shortcuts import redirect, render
from .models import User
from .forms import EmployeeForm

def create_employee(request):
    admin_id = request.session.get('admin_id')
    if not admin_id:
        return redirect('login')

    try:
        admin = User.objects.get(id=admin_id, access='admin')
    except User.DoesNotExist:
        return redirect('login')

    if request.method == 'POST':
        form = EmployeeForm(request.POST, request.FILES)
        if form.is_valid():
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            role = form.cleaned_data['role']
            shift = form.cleaned_data.get('shift')
            reporting_manager = form.cleaned_data.get('reporting_manager')
            employee_id = form.cleaned_data.get('employee_id')
            access = form.cleaned_data.get('access')
            profile_image = form.cleaned_data.get('profile_image')
            teams_chat_link = form.cleaned_data.get('teams_chat_link')

            username = email.split('@')[0]
            password = get_random_string(length=10)  # WARNING: plain text

            if User.objects.filter(username=username).exists():
                messages.error(request, f"Username '{username}' already exists. Please use a different email.")
                return render(request, 'accounts/create_employee.html', {'form': form, 'admin': admin})

            user = User.objects.create(
                name=name,
                email=email,
                username=username,
                password=password,  # ⚠️ WARNING: switch to hashed for production
                role=role,
                shift=shift,
                reporting_manager=reporting_manager,
                employee_id=employee_id,
                access=access,
                profile_image=profile_image if profile_image else 'profile_images/default.jpg',
                teams_chat_link=teams_chat_link,
                status='logged off',
            )

            send_mail(
                subject='Your NeatNest Login Credentials',
                message=f'Hi {name},\n\nYour login credentials are:\nUsername: {username}\nPassword: {password}\n\nPlease log in and change your password.',
                from_email='noreply@neatnest.com',
                recipient_list=[email],
                fail_silently=True,
            )

            # messages.success(request, f"Employee '{username}' created successfully.")
            # return redirect('home')
        else:
            messages.error(request, "Form contains errors. Please fix and submit again.")
    else:
        form = EmployeeForm()

    return render(request, 'accounts/create_employee.html', {'form': form, 'user': admin})


 
from django.views.decorators.http import require_POST
from django.http import JsonResponse
from .models import User
from django.shortcuts import render, redirect
from django.contrib import messages
from .models import User


def status_view(request):
    user = User.objects.get(id=request.session.get('user_id'))

    if request.method == 'POST':
        status = request.POST.get('status')
        shift = request.POST.get('shift')

        if status and shift:
            user.status = status
            user.shift = shift
            user.save()
            messages.success(request, "Updated successfully")
            return redirect('status')

        messages.error(request, "Please select both status and shift")

    return render(request, 'accounts/status.html', {'user': user})

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
 




def notice_view(request):
    return render(request, 'accounts/notice.html')



 
from django.shortcuts import render, redirect, get_object_or_404
from .forms import EmployeeForm
from .models import User
from .forms import ProfileImageForm
 
 
 
def view_profile(request):
    user_id = request.session.get('user_id')
    if not user_id:
        return redirect('login')
 
    try:
        user = User.objects.get(id=user_id)
    except User.DoesNotExist:
        return redirect('login')
 
    if request.method == 'POST':
        form = ProfileImageForm(request.POST, request.FILES, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, "Profile image updated.")
            return redirect('view_profile')
    else:
        form = ProfileImageForm(instance=user)
 
    context = {
        'user': user,
        'form': form
    }
    return render(request, 'accounts/profile_page.html', context)
 
 
 
from django.views.decorators.csrf import csrf_exempt
from django.http import JsonResponse
from .models import User
 
@csrf_exempt  # Optional if you're passing CSRF token via JS
def upload_profile_image(request):
    if request.method == 'POST' and request.FILES.get('profile_image'):
        user_id = request.session.get('user_id')
        user = get_object_or_404(User, id=user_id)
 
        user.profile_image = request.FILES['profile_image']
        user.save()
        return JsonResponse({
            'success': True,
            'image_url': user.profile_image.url
        })
    return JsonResponse({'success': False})
 


import os
import numpy as np
import pandas as pd
from django.shortcuts import render, redirect
from django.conf import settings
from django.contrib import messages
 
TICKET_EXCEL = os.path.join(settings.MEDIA_ROOT, 'Book.xlsx')
SUBMIT_EXCEL = os.path.join(settings.MEDIA_ROOT, 'Submitted_Shift_End.xlsx')
 
def shift_end_email(request):
    ticket = None
    comment = ""
    searched = False
 
    if request.method == 'POST':
        print("POST method triggered.")
        if 'submit_action' in request.POST:
            # Handle submission
            print("Submit action detected.")
            ticket_id = request.POST.get('ticket_id', '').strip()
            comment = request.POST.get('comment', '').strip()
            action = request.POST.get('action', '').strip()
 
            print(f"ticket_id: {ticket_id}, comment: {comment}, action: {action}")
     
            if not ticket_id:
                print("No ticket ID submitted.")
                messages.warning(request, "Ticket ID is required for submission.")
                return redirect('shift_end_email')
 
            try:
                df = pd.read_excel(TICKET_EXCEL, engine='openpyxl')
                print("Loaded Book.xlsx successfully.")
            except Exception as e:
                print(f"Error loading ticket Excel: {e}")
                messages.error(request, f"Error loading ticket Excel: {e}")
                return redirect('shift_end_email')
 
            # Clean columns
            df.columns = df.columns.str.replace('\xa0', ' ', regex=True)
            df.columns = df.columns.str.encode('ascii', 'ignore').str.decode('utf-8')
            df.columns = df.columns.str.strip()
 
            if 'Comment' not in df.columns:
                df['Comment'] = ""
            if 'Action' not in df.columns:
                df['Action'] = ""
 
       
 
            match_index = df[df['Ticket ID'].astype(str) == ticket_id].index
 
            if match_index.empty:
                print("Ticket ID not found in Book.xlsx.")
                messages.warning(request, "Ticket ID not found for submission.")
                return redirect('shift_end_email')
 
            index = match_index[0]
            df.at[index, 'Comment'] = comment
            df.at[index, 'Action'] = action
            print("Updated comment and action in df.")
 
 
            try:
                df.to_excel(TICKET_EXCEL, index=False, engine='openpyxl')
                print("Saved updates to Book.xlsx.")
            except Exception as e:
                print(f"Error saving updated ticket Excel: {e}")
                messages.error(request, f"Error saving updated ticket Excel: {e}")
                return redirect('shift_end_email')
 
            submission_data = df.loc[[index]]
            print("Submission row to be added:\n", submission_data)
 
            if os.path.exists(SUBMIT_EXCEL):
                try:
                    existing_submissions = pd.read_excel(SUBMIT_EXCEL, engine='openpyxl')
                    print("Loaded existing Submitted_Shift_End.xlsx")
                    updated_submissions = pd.concat([existing_submissions, submission_data], ignore_index=True)
                except Exception as e:
                    print(f"Error reading existing submissions: {e}")
                    messages.error(request, f"Error reading existing submissions: {e}")
                    return redirect('shift_end_email')
            else:
                print("Submitted_Shift_End.xlsx doesn't exist. Creating new.")
                updated_submissions = submission_data
 
            try:
                updated_submissions.to_excel(SUBMIT_EXCEL, index=False, engine='openpyxl')
                print(f"Written to {SUBMIT_EXCEL}. Final rows: {len(updated_submissions)}")
            except Exception as e:
                print(f"Error writing to submission Excel: {e}")
                messages.error(request, f"Error writing to submission Excel: {e}")
                return redirect('shift_end_email')
 
            messages.success(request, "Ticket updated and submission recorded.")
            # Redirect with ticket_id query param to show updated data after submission
            return redirect(f'{request.path}?ticket_id={ticket_id}')
           
 
        else:
            # Handle search submit
            ticket_id = request.POST.get('ticket_id', '').strip()
            if not ticket_id:
                messages.warning(request, "Ticket ID is required to search.")
                return redirect('shift_end_email')
 
            searched = True
 
            try:
                df = pd.read_excel(TICKET_EXCEL, engine='openpyxl')
            except Exception as e:
                messages.error(request, f"Error loading ticket Excel: {e}")
                return redirect('shift_end_email')
 
            df.columns = df.columns.str.replace('\xa0', ' ', regex=True)
            df.columns = df.columns.str.encode('ascii', 'ignore').str.decode('utf-8')
            df.columns = df.columns.str.strip()
 
            for col in df.select_dtypes(include=['datetimetz', 'datetime64[ns, UTC]']).columns:
                df[col] = df[col].dt.tz_localize(None)
 
            df = df.replace({pd.NaT: '', np.nan: ''})
 
            match = df[df['Ticket ID'].astype(str) == ticket_id]
            if not match.empty:
                ticket = match.iloc[0].to_dict()
                comment = ticket.get('Comment', '')
 
            return render(request, 'accounts/shift_end_email.html', {
                'ticket': ticket,
                'comment': comment,
                'ticket_id': ticket_id,
                'searched': searched
            })
 
    else:
        # GET method — check for ticket_id in query param, if exists show ticket info
        ticket_id = request.GET.get('ticket_id', '').strip()
        searched = False
 
        if ticket_id:
            searched = True
            try:
                df = pd.read_excel(TICKET_EXCEL, engine='openpyxl')
            except Exception as e:
                messages.error(request, f"Error loading ticket Excel: {e}")
                return render(request, 'accounts/shift_end_email.html', {
                    'ticket': None,
                    'comment': '',
                    'ticket_id': '',
                    'searched': False
                })
 
            df.columns = df.columns.str.replace('\xa0', ' ', regex=True)
            df.columns = df.columns.str.encode('ascii', 'ignore').str.decode('utf-8')
            df.columns = df.columns.str.strip()
 
            for col in df.select_dtypes(include=['datetimetz', 'datetime64[ns, UTC]']).columns:
                df[col] = df[col].dt.tz_localize(None)
 
            df = df.replace({pd.NaT: '', np.nan: ''})
 
            match = df[df['Ticket ID'].astype(str) == ticket_id]
            if not match.empty:
                ticket = match.iloc[0].to_dict()
                comment = ticket.get('Comment', '')
 
        return render(request, 'accounts/shift_end_email.html', {
            'ticket': ticket,
            'comment': comment,
            'ticket_id': ticket_id,
            'searched': searched
        })
 
import pandas as pd
from django.shortcuts import render
from django.conf import settings
import os
 
SUBMIT_EXCEL = os.path.join(settings.MEDIA_ROOT, 'Submitted_Shift_End.xlsx')
 
def submitted_shift_end(request):
    try:
        df = pd.read_excel(SUBMIT_EXCEL, dtype=str)  # Read all as string
        df.columns = df.columns.str.strip()
 
        print("RAW DF:\n", df)  # 👈 print raw data
 
        # Normalize Action field (optional for consistency, even though we don’t filter now)
        df['Action'] = df['Action'].str.strip().str.lower()
 
        # Do NOT filter — show all submitted records
        data = df.fillna("").to_dict(orient='records')
    except Exception as e:
        print("Error reading Excel:", e)
        data = []
 
    return render(request, 'accounts/submitted_shift_end.html', {'data': data})
 
 

##############


