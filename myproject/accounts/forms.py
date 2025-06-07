from django import forms
from .models import User, ACCESS_CHOICES
from .models import REPORTING_MANAGER_CHOICES


class EmployeeForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    role = forms.CharField(max_length=50)
    shift = forms.CharField(max_length=10, required=False)
    

    reporting_manager = forms.ChoiceField(
    choices=[('', '-- Select Manager --')] + REPORTING_MANAGER_CHOICES,
    required=False,
    label='Reporting Manager'
)

    employee_id = forms.CharField(max_length=20, required=False)
    access = forms.ChoiceField(choices=User._meta.get_field('access').choices, initial='guest')
    profile_image = forms.ImageField(required=False)  # optional image upload
    teams_chat_link = forms.URLField(required=False, label='Teams Chat Link')


class ProfileImageForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['profile_image']
