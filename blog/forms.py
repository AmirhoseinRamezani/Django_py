from django import forms
from blog.models import Comment
from captcha.fields import CaptchaField

class CommentForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        self.user = kwargs.pop('user', None)
        super(CommentForm, self).__init__(*args, **kwargs)
        
        if self.user and self.user.is_authenticated:
            self.fields.pop('name', None)
            self.fields.pop('email', None)
            self.fields.pop('captcha', None)
        else:
            self.fields['captcha'] = CaptchaField(
                label='کد امنیتی',
                error_messages={'invalid': 'کد امنیتی وارد شده صحیح نیست'}
            )
    
    class Meta:
        model = Comment
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Your Name'
            }),
            'email': forms.EmailInput(attrs={
                'class': 'form-control',
                'placeholder': 'Email Address'
            }),
            'subject': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Subject'
            }),
            'message': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Your Message',
                'rows': 5
            }),
        }