
# accounts/forms.py
from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from .models import UserProfile

class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    
    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']
    
    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        if commit:
            user.save()
        return user

class CustomAuthenticationForm(AuthenticationForm):
    username = forms.CharField(
        label='نام کاربری یا ایمیل',
        widget=forms.TextInput(attrs={'class': 'form-control'})
    )
    password = forms.CharField(
        label='رمز عبور',
        widget=forms.PasswordInput(attrs={'class': 'form-control'})
    )

class UserUpdateForm(forms.ModelForm):
    email = forms.EmailField()
    
    class Meta:
        model = User
        fields = ['username', 'first_name', 'last_name', 'email']

class ProfileUpdateForm(forms.ModelForm):
    class Meta:
        model = UserProfile
        fields = [
            'profile_image', 
            'bio', 
            'phone_number', 
            'birth_date',
            'education_level',
            'field_of_study',
            'job_title',
            'company',
            'website',
            'github',
            'linkedin',
            'twitter',
            'instagram'
        ]
        widgets = {
            'birth_date': forms.DateInput(attrs={'type': 'date'}),
            'bio': forms.Textarea(attrs={'rows': 4, 'placeholder': 'درباره خودتان بنویسید...'}),
            'phone_number': forms.TextInput(attrs={'placeholder': '09123456789'}),
        }
        labels = {
            'profile_image': 'تصویر پروفایل',
            'bio': 'بیوگرافی',
            'phone_number': 'شماره تلفن',
            'birth_date': 'تاریخ تولد',
            'education_level': 'سطح تحصیلات',
            'field_of_study': 'رشته تحصیلی',
            'job_title': 'عنوان شغلی',
            'company': 'شرکت',
            'website': 'وبسایت',
            'github': 'GitHub',
            'linkedin': 'LinkedIn',
            'twitter': 'Twitter',
            'instagram': 'Instagram',
        }
        