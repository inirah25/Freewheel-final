from django import forms

class EmployeeForm(forms.Form):
    name = forms.CharField(max_length=100)
    email = forms.EmailField()
    role = forms.CharField(max_length=50)
