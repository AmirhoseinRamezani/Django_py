# tours/views.py
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from .models import Tour, TourCategory, TourBooking, Seat, Transportation
from .forms import TourSearchForm, TourBookingForm

def tour_list(request):
    tours = Tour.objects.filter(is_active=True)
    
    # فیلترها
    category = request.GET.get('category')
    tour_type = request.GET.get('type')
    destination = request.GET.get('destination')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')
    
    if category:
        tours = tours.filter(category__slug=category)
    if tour_type:
        tours = tours.filter(tour_type=tour_type)
    if destination:
        tours = tours.filter(destination__slug=destination)
    if min_price:
        tours = tours.filter(price__gte=min_price)
    if max_price:
        tours = tours.filter(price__lte=max_price)
    
    # صفحه‌بندی
    from django.core.paginator import Paginator
    paginator = Paginator(tours, 9)
    page_number = request.GET.get('page')
    tours_page = paginator.get_page(page_number)
    
    categories = TourCategory.objects.all()
    
    context = {
        'tours': tours_page,
        'categories': categories,
    }
    return render(request, 'tours/tour_list.html', context)

def tour_detail(request, slug):
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    related_tours = Tour.objects.filter(
        category=tour.category, 
        is_active=True
    ).exclude(id=tour.id)[:4]
    
    context = {
        'tour': tour,
        'related_tours': related_tours,
    }
    return render(request, 'tours/tour_detail.html', context)
@login_required
def tour_booking(request, pk):
    tour = get_object_or_404(Tour, pk=pk, is_active=True)
    
    if request.method == 'POST':
        form = TourBookingForm(request.POST, tour=tour)
        if form.is_valid():
            try:
                # ایجاد رزرو
                booking = form.save(commit=False)
                booking.user = request.user
                booking.tour = tour
                booking.total_price = tour.get_current_price() * form.cleaned_data['passenger_count']
                booking.save()
                
                # انتخاب صندلی‌ها
                selected_seat_ids = request.POST.getlist('selected_seats')
                for i, seat_id in enumerate(selected_seat_ids):
                    seat = Seat.objects.get(id=seat_id)
                    SelectedSeat.objects.create(
                        booking=booking,
                        seat=seat,
                        passenger_name=form.cleaned_data[f'passenger_{i}_name'],
                        passenger_age=form.cleaned_data[f'passenger_{i}_age']
                    )
                    # غیرفعال کردن صندلی رزرو شده
                    seat.is_available = False
                    seat.save()
                
                # به‌روزرسانی صندلی‌های خالی تور
                tour.available_seats = tour.transportation.seats.filter(is_available=True).count()
                tour.save()
                
                messages.success(request, 'رزرو تور شما با موفقیت ثبت شد!')
                return redirect('tours:booking_detail', booking_id=booking.id)
                
            except Exception as e:
                messages.error(request, f'خطا در ثبت رزرو: {str(e)}')
    else:
        form = TourBookingForm(tour=tour)
    
    context = {
        'tour': tour,
        'form': form,
    }
    return render(request, 'tours/booking.html', context)

def get_available_seats(request, tour_id):
    tour = get_object_or_404(Tour, id=tour_id)
    seats = []
    
    if tour.transportation:
        seats = list(tour.transportation.seats.filter(is_available=True).values(
            'id', 'seat_number', 'seat_class', 'row', 'column', 
            'window_seat', 'aisle_seat', 'extra_legroom'
        ))
    
    return JsonResponse({'seats': seats})