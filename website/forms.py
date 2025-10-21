# website/forms.py
from django import forms
from website.models import Contact,NewsletterSubscriber
from captcha.fields import CaptchaField

class NameForm(forms.Form):
    name= forms.CharField(max_length=100,label='نام شما')
    email= forms.EmailField()
    subject=forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
    
class ContactForm(forms.ModelForm):
    class ContactForm(forms.Form):
        name = forms.CharField(
            max_length=100,
            widget=forms.TextInput(attrs={
                'class': 'common-input mb-20 form-control',
                'placeholder': 'Enter your name'
            })
        )
        email = forms.EmailField(
            widget=forms.EmailInput(attrs={
                'class': 'common-input mb-20 form-control',
                'placeholder': 'Enter email address'
            })
        )
        subject = forms.CharField(
            max_length=200,
            widget=forms.TextInput(attrs={
                'class': 'common-input mb-20 form-control',
                'placeholder': 'Enter subject'
            })
        )
        message = forms.CharField(
            widget=forms.Textarea(attrs={
                'class': 'common-textarea form-control',
                'placeholder': 'Enter Message',
                'rows': 5
            })
        )
    captcha = CaptchaField()
    class Meta: 
        model = Contact
        fields = ['name', 'email', 'subject', 'message']
        labels = {
            'name': 'نام',
            'email': 'ایمیل', 
            'subject': 'موضوع',
            'message': 'پیام'
        }
        
# class NewsletterForm(forms.ModelForm):
    
#     class Meta:
#         model = Newsletter
#         fields = '__all__'
class NewsletterForm(forms.ModelForm):
    class Meta:
        model = NewsletterSubscriber
        fields = ['email']
        widgets = {
            'email': forms.EmailInput(attrs={
                'placeholder': 'ایمیل خود را وارد کنید',
                'class': 'form-control'
            })
        }
        labels = {
            'email': ''
        }