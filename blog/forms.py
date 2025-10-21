from django import forms
from blog.models import Comment
# from captcha.fields import CaptchaField

class CommentForm(forms.ModelForm):
    # captcha = CaptchaField()
    
    class Meta: 
        model = Comment
        fields = ['post', 'name', 'email', 'subject', 'message']
        widgets = {
            'post': forms.HiddenInput(),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Enter Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control', 
                'placeholder': 'Enter email address'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control mb-10',
                'rows': 5,
                'placeholder': 'Message'
            })
        }
        labels = {
            'name': 'نام',
            'email': 'ایمیل', 
            'subject': 'موضوع',
            'message': 'پیام'
        }