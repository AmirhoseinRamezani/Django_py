from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.db.models import Q
from django.http import JsonResponse
from django.core.paginator import Paginator
from django.utils import timezone
from .models import Tour, TourCategory, TourBooking, Seat, Passenger, Discount
from .forms import TourSearchForm, TourBookingForm
from decimal import Decimal


def tour_list(request):
    """لیست تورها با فیلترهای پیشرفته - نسخه اصلاح شده"""
    try:
        # ابتدا بررسی می‌کنیم فیلد departure_datetime وجود دارد یا نه
        tours = Tour.objects.filter(is_active=True)
        
        # اگر فیلد departure_datetime وجود دارد، فیلتر زمانی اعمال کن
        if hasattr(Tour.objects.first(), 'departure_datetime'):
            tours = tours.filter(departure_datetime__gte=timezone.now())
        else:
            # اگر فیلد وجود ندارد، فقط تورهای فعال را نشان بده
            tours = tours.filter(is_active=True)
            messages.warning(request, 'سیستم در حال به‌روزرسانی است. برخی امکانات موقتاً غیرفعال هستند.')
        
        # اعمال فیلترها
        form = TourSearchForm(request.GET)
        if form.is_valid():
            destination = form.cleaned_data.get('destination')
            category = form.cleaned_data.get('category')
            min_price = form.cleaned_data.get('min_price')
            max_price = form.cleaned_data.get('max_price')
            
            if destination:
                tours = tours.filter(
                    Q(destination_city__icontains=destination) | 
                    Q(origin_city__icontains=destination)
                )
            if category:
                tours = tours.filter(category=category)
            if min_price:
                tours = tours.filter(base_price__gte=min_price)
            if max_price:
                tours = tours.filter(base_price__lte=max_price)
        
        # مرتب‌سازی ایمن
        sort_by = request.GET.get('sort', '-created_at')  # تغییر به created_at به عنوان پیش‌فرض
        
        # فقط اگر فیلد وجود دارد، مرتب‌سازی کن
        if hasattr(Tour.objects.first(), 'departure_datetime') and sort_by in ['-departure_datetime', 'departure_datetime']:
            tours = tours.order_by(sort_by)
        elif sort_by in ['base_price', '-base_price'] and hasattr(Tour.objects.first(), 'base_price'):
            tours = tours.order_by(sort_by)
        else:
            tours = tours.order_by('-created_at')
        
        # صفحه‌بندی
        paginator = Paginator(tours, 12)
        page_number = request.GET.get('page')
        tours_page = paginator.get_page(page_number)
        
        categories = TourCategory.objects.filter(is_active=True)
        
        context = {
            'tours': tours_page,
            'categories': categories,
            'form': form,
            'sort_by': sort_by,
        }
        return render(request, 'tours/tour_list.html', context)
        
    except Exception as e:
        # اگر خطایی رخ داد، صفحه خطا نمایش داده شود
        return render(request, 'tours/error.html', {
            'message': 'سیستم در حال به‌روزرسانی است. لطفاً چند دقیقه دیگر تلاش کنید.'
        })

def tour_detail(request, slug):
    """صفحه جزئیات تور - نسخه اصلاح شده"""
    """صفحه جزئیات تور با قابلیت خرید"""
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    
    # محاسبه قیمت نهایی با تخفیف
    final_price = tour.get_current_price()
    has_discount = tour.discount_price is not None and tour.discount_price < tour.base_price
    
    # تورهای مرتبط
    related_tours = Tour.objects.filter(
        category=tour.category, 
        is_active=True,
        departure_datetime__gte=timezone.now()
    ).exclude(id=tour.id)[:4]
    
    # بررسی امکان رزرو
    can_book = (
        tour.available_capacity > 0 and 
        tour.departure_datetime > timezone.now()
    )
    
    context = {
        'tour': tour,
        'related_tours': related_tours,
        'can_book': can_book,
        'final_price': final_price,
        'has_discount': has_discount,
        'discount_amount': tour.base_price - final_price if has_discount else Decimal('0'),
        'includes_list': tour.get_includes_list(),
        'excludes_list': tour.get_excludes_list(),
        'user_authenticated': request.user.is_authenticated,
    }
    return render(request, 'tours/tour_detail.html', context)

@login_required
def quick_booking(request, slug):
    """رزرو سریع تور"""
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    
    if request.method == 'POST':
        adult_count = int(request.POST.get('adult_count', 1))
        
        # بررسی ظرفیت
        if tour.available_capacity < adult_count:
            messages.error(request, 'ظرفیت کافی موجود نیست.')
            return redirect('tours:tour_detail', slug=slug)
        
        try:
            # ایجاد رزرو
            booking = TourBooking.objects.create(
                user=request.user,
                tour=tour,
                adult_count=adult_count,
                child_count=0,
                infant_count=0,
                base_amount=tour.get_current_price() * adult_count,
                total_amount=tour.get_current_price() * adult_count,
                status='pending'
            )
            
            # کاهش ظرفیت
            tour.available_capacity -= adult_count
            tour.save()
            
            messages.success(request, f'رزرو شما با کد {booking.booking_reference} ثبت شد!')
            return redirect('tours:booking_detail', booking_reference=booking.booking_reference)
            
        except Exception as e:
            messages.error(request, f'خطا در ثبت رزرو: {str(e)}')
    
    return redirect('tours:tour_detail', slug=slug)
        
    # except Exception as e:
    #     return render(request, 'tours/error.html', {
    #         'message': 'تور مورد نظر یافت نشد.'
    #     })

@login_required
def tour_booking(request, slug):
    """صفحه رزرو تور"""
    tour = get_object_or_404(Tour, slug=slug, is_active=True)
    
    # بررسی شرایط رزرو
    if tour.available_capacity <= 0:
        messages.error(request, 'متأسفانه این تور تکمیل شده است.')
        return redirect('tours:tour_detail', slug=slug)
    
    if tour.departure_datetime <= timezone.now():
        messages.error(request, 'زمان رزرو این تور به پایان رسیده است.')
        return redirect('tours:tour_detail', slug=slug)
    
    if request.method == 'POST':
        form = TourBookingForm(request.POST, tour=tour)
        if form.is_valid():
            try:
                # ایجاد رزرو
                booking = form.save(commit=False)
                booking.user = request.user
                booking.tour = tour
                
                # محاسبه قیمت
                adult_count = form.cleaned_data['adult_count']
                child_count = form.cleaned_data['child_count']
                infant_count = form.cleaned_data['infant_count']
                
                base_amount = (
                    adult_count * tour.base_price +
                    (child_count * tour.child_price if tour.child_price else 0) +
                    (infant_count * tour.infant_price if tour.infant_price else 0)
                )
                
                booking.base_amount = base_amount
                booking.total_amount = base_amount - booking.discount_amount
                booking.save()
                
                # افزودن مسافرین
                for i in range(adult_count + child_count + infant_count):
                    passenger_type = 'adult' if i < adult_count else 'child' if i < adult_count + child_count else 'infant'
                    Passenger.objects.create(
                        booking=booking,
                        first_name=form.cleaned_data[f'passenger_{i}_first_name'],
                        last_name=form.cleaned_data[f'passenger_{i}_last_name'],
                        date_of_birth=form.cleaned_data[f'passenger_{i}_birth_date'],
                        gender=form.cleaned_data[f'passenger_{i}_gender'],
                        passenger_type=passenger_type
                    )
                
                # به‌روزرسانی ظرفیت تور
                tour.available_capacity -= (adult_count + child_count + infant_count)
                tour.save()
                
                messages.success(request, f'رزرو شما با کد {booking.booking_reference} ثبت شد!')
                return redirect('tours:booking_detail', booking_reference=booking.booking_reference)
                
            except Exception as e:
                messages.error(request, f'خطا در ثبت رزرو: {str(e)}')
    else:
        form = TourBookingForm(tour=tour)
    
    context = {
        'tour': tour,
        'form': form,
    }
    return render(request, 'tours/tour_booking.html', context)

@login_required
def booking_detail(request, booking_reference):
    """جزئیات رزرو"""
    booking = get_object_or_404(
        TourBooking, 
        booking_reference=booking_reference,
        user=request.user
    )
    
    context = {
        'booking': booking,
        'passengers': booking.passengers.all(),
    }
    return render(request, 'tours/booking_detail.html', context)

def get_available_seats(request, tour_id):
    """دریافت صندلی‌های خالی برای تور"""
    tour = get_object_or_404(Tour, id=tour_id)
    
    if not tour.departure_transportation:
        return JsonResponse({'seats': []})
    
    seats = tour.departure_transportation.seats.filter(
        is_available=True,
        is_active=True
    ).values('id', 'seat_number', 'seat_class', 'row', 'column', 'features', 'price_modifier')
    
    return JsonResponse({'seats': list(seats)})

def apply_discount(request):
    """اعمال کد تخفیف"""
    if request.method == 'POST':
        discount_code = request.POST.get('discount_code')
        tour_id = request.POST.get('tour_id')
        
        try:
            discount = Discount.objects.get(
                code=discount_code,
                is_active=True,
                valid_from__lte=timezone.now().date(),
                valid_to__gte=timezone.now().date()
            )
            
            tour = Tour.objects.get(id=tour_id)
            
            if discount.can_apply_to_tour(tour):
                return JsonResponse({
                    'success': True,
                    'discount_amount': float(discount.value),
                    'message': 'کد تخفیف اعمال شد'
                })
            else:
                return JsonResponse({
                    'success': False,
                    'message': 'این کد تخفیف برای این تور قابل استفاده نیست'
                })
                
        except Discount.DoesNotExist:
            return JsonResponse({
                'success': False,
                'message': 'کد تخفیف نامعتبر است'
            })
    
    return JsonResponse({'success': False, 'message': 'درخواست نامعتبر'})