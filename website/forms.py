# website/forms.py
from django import forms
from website.models import Contact,NewsletterSubscriber


class NameForm(forms.Form):
    name= forms.CharField(max_length=100,label='نام شما')
    email= forms.EmailField()
    subject=forms.CharField(max_length=255)
    message = forms.CharField(widget=forms.Textarea)
    
class ContactForm(forms.ModelForm):
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