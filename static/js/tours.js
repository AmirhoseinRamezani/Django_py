// مدیریت انتخاب صندلی
document.addEventListener('DOMContentLoaded', function() {
    // انتخاب صندلی
    const seatElements = document.querySelectorAll('.seat-select');
    
    seatElements.forEach(seat => {
        seat.addEventListener('click', function() {
            const seatId = this.dataset.seatId;
            const isSelected = this.classList.contains('selected');
            
            if (isSelected) {
                this.classList.remove('selected');
                removeSeatFromSelection(seatId);
            } else {
                this.classList.add('selected');
                addSeatToSelection(seatId);
            }
        });
    });
    
    // اعمال کد تخفیف
    const discountForm = document.getElementById('discount-form');
    if (discountForm) {
        discountForm.addEventListener('submit', function(e) {
            e.preventDefault();
            applyDiscountCode();
        });
    }
});

function addSeatToSelection(seatId) {
    // اضافه کردن صندلی به لیست انتخاب‌شده
}

function removeSeatFromSelection(seatId) {
    // حذف صندلی از لیست انتخاب‌شده
}

function applyDiscountCode() {
    // ارسال درخواست اعمال تخفیف
}