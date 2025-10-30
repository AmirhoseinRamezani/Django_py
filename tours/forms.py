# tours/forms.py
from django import forms
from .models import TourBooking, Tour, TourCategory

class TourSearchForm(forms.Form):
    destination = forms.CharField(required=False, label='مقصد')
    category = forms.ModelChoiceField(
        queryset=TourCategory.objects.filter(is_active=True),
        required=False,
        label='دسته‌بندی'
    )
    min_price = forms.DecimalField(required=False, label='حداقل قیمت')
    max_price = forms.DecimalField(required=False, label='حداکثر قیمت')
    departure_date = forms.DateField(required=False, label='تاریخ حرکت')

class TourBookingForm(forms.ModelForm):
    class Meta:
        model = TourBooking
        fields = ['adult_count', 'child_count', 'infant_count', 'special_requests']
    
    def __init__(self, *args, **kwargs):
        self.tour = kwargs.pop('tour', None)
        super().__init__(*args, **kwargs)