from django import forms
from django.contrib.auth.forms import PasswordChangeForm
from .models import *

class RegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ('full_name', 'username', 'email', 'password', 'role', 'image',)

class LoginForm(forms.Form):
    email = forms.EmailField()
    password = forms.CharField(widget=forms.PasswordInput)

class AssignmentForm(forms.ModelForm):
    deadline = forms.DateTimeField(widget=forms.DateTimeInput(attrs={'type': 'datetime-local'}))
    class Meta:
        model = Assignment
        fields = ('title', 'description', 'deadline', 'semester', 'departement', 'attachment')

class StudentProfileAndPasswordForm(forms.ModelForm):
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput, required=False)

    class Meta:
        model = CustomUser
        fields = ['full_name','username','email', 'nidn', 'address', 'phone_number', 'image']

class DateFilterForm(forms.Form):
    start_date = forms.DateField(label='Tanggal Mulai', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='Tanggal Selesai', required=False, widget=forms.DateInput(attrs={'type': 'date'}))

class AssignmentFilterForm(forms.Form):
    STATUS_CHOICES = [
        ('all', 'Semua'),
        ('graded', 'Sudah Dinilai'),
        ('ungraded', 'Belum Dinilai')
    ]

    start_date = forms.DateField(label='Tanggal Mulai', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(label='Tanggal Selesai', required=False, widget=forms.DateInput(attrs={'type': 'date'}))
    status = forms.ChoiceField(label='Status', choices=STATUS_CHOICES, required=False)

class DsnProfileAndPasswordForm(forms.ModelForm):
    new_password1 = forms.CharField(label="New Password", widget=forms.PasswordInput, required=False)
    new_password2 = forms.CharField(label="Confirm New Password", widget=forms.PasswordInput, required=False)
    nidn = forms.CharField(label='NIDN', widget=forms.TextInput, disabled=True)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'username','nidn', 'email', 'department', 'address', 'phone_number']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['department'].widget = forms.Select(choices=CustomUser.DEPARTMENT_CHOICES)

class AssignmentSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('attachment',)


class EditSubmissionForm(forms.ModelForm):
    class Meta:
        model = Submission
        fields = ('attachment',)

class AssignmentGradeForm(forms.ModelForm):
    class Meta:
        model = AssignmentGrade
        fields = ['grade', 'feedback']

    def __init__(self, *args, **kwargs):
        super(AssignmentGradeForm, self).__init__(*args, **kwargs)
        self.fields['grade'].widget.attrs['min'] = 0
        self.fields['grade'].widget.attrs['max'] = 100
        self.fields['grade'].widget.attrs['step'] = 0.01