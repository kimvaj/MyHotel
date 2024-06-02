from django.db import models
from common.basemodel import BaseModel
from datetime import date

class Hotel(BaseModel):
    name = models.CharField(max_length=150)
    address = models.CharField(max_length=255)
    village = models.CharField(max_length=100)
    district = models.CharField(max_length=100)
    province = models.CharField(max_length=100)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    stars = models.PositiveSmallIntegerField()
    check_in_time = models.TimeField()
    check_out_time = models.TimeField()

    def __str__(self):
        return self.name

    def get_available_rooms(self):
        return self.room_hotel.filter(status=Room.AVAILABLE).count()

    def get_staff_count(self):
        return self.staff_hotel.count()

    def get_average_rating(self):
        # Assuming there's a Rating model related to Hotel
        ratings = self.rating_set.all()
        return ratings.aggregate(models.Avg('score'))['score__avg'] if ratings else None


class Staff(BaseModel):
    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='staff_hotel')
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    position = models.CharField(max_length=100)
    salary = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    date_of_birth = models.DateField()
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)
    hire_date = models.DateField()

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_age(self):
        return date.today().year - self.date_of_birth.year

    def get_years_of_service(self):
        return date.today().year - self.hire_date.year


class Guest(BaseModel):
    first_name = models.CharField(max_length=100)
    last_name = models.CharField(max_length=100)
    date_of_birth = models.DateField()
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20)
    email = models.EmailField(max_length=255)

    def __str__(self):
        return f'{self.first_name} {self.last_name}'

    def get_current_bookings(self):
        return self.booking_guest.filter(check_out_date__gte=date.today())

    def get_booking_history(self):
        return self.booking_guest.filter(check_out_date__lt=date.today())


class RoomType(BaseModel):
    name = models.CharField(max_length=50)
    description = models.CharField(max_length=255)
    price_per_night = models.DecimalField(max_digits=9, decimal_places=2, default=0)
    capacity = models.PositiveSmallIntegerField()
    image = models.ImageField(upload_to='images')

    def __str__(self):
        return self.name

    def get_total_revenue(self):
        return sum(booking.total_price for booking in self.room_type.all())


class Room(BaseModel):
    AVAILABLE = 'available'
    OCCUPIED = 'occupied'

    STATUS_CHOICES = [
        (AVAILABLE, 'Available'),
        (OCCUPIED, 'Occupied'),
    ]

    hotel = models.ForeignKey(Hotel, on_delete=models.CASCADE, related_name='room_hotel')
    room_type = models.ForeignKey(RoomType, on_delete=models.CASCADE, related_name='room_type')
    room_number = models.CharField(max_length=15, unique=True)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=AVAILABLE)

    def __str__(self):
        return self.room_number

    def is_available(self):
        return self.status == Room.AVAILABLE

    def change_status(self, new_status):
        self.status = new_status
        self.save()



# class Booking(BaseModel):
#     guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='booking_guest')
#     room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='booking_room')
#     check_in_date = models.DateField()
#     check_out_date = models.DateField()
#     total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

#     def __str__(self):
#         return f'Booking {self.id} for {self.guest} in room {self.room}'

#     def save(self, *args, **kwargs):
#         if self.check_in_date >= self.check_out_date:
#             raise ValueError("Check-in date must be before check-out date.")
#         self.total_price = self.calculate_total_price()
#         super().save(*args, **kwargs)

#     def calculate_total_price(self):
#         price_per_night = self.room.room_type.price_per_night
#         total_nights = (self.check_out_date - self.check_in_date).days
#         return total_nights * price_per_night

#     def get_total_paid(self):
#         return self.payment_booking.aggregate(total_paid=models.Sum('amount'))['total_paid'] or 0

#     def get_outstanding_balance(self):
#         return self.total_price - self.get_total_paid()
class Booking(BaseModel):
    guest = models.ForeignKey(Guest, on_delete=models.CASCADE, related_name='booking_guest')
    room = models.ForeignKey(Room, on_delete=models.CASCADE, related_name='booking_room')
    check_in_date = models.DateField()
    check_out_date = models.DateField(blank=True)
    total_price = models.DecimalField(max_digits=9, decimal_places=2, default=0)

    def __str__(self):
        return f'Booking {self.id} for {self.guest} in room {self.room}'

    def save(self, *args, **kwargs):
        if self.check_in_date >= self.check_out_date:
            raise ValueError("Check-in date must be before check-out date.")
        self.total_price = self.calculate_total_price()
        super().save(*args, **kwargs)

    def calculate_total_price(self):
        price_per_night = self.room.room_type.price_per_night
        total_nights = (self.check_out_date - self.check_in_date).days
        return total_nights * price_per_night

    def get_total_paid(self):
        total_paid = self.payment_booking.aggregate(models.Sum('amount'))['amount__sum']
        return total_paid if total_paid is not None else 0


class Payment(BaseModel):
    PAYMENT_METHOD_CASH = 'cash'
    PAYMENT_METHOD_CREDIT_CARD = 'credit_card'
    PAYMENT_METHOD_DEBIT_CARD = 'debit_card'
    PAYMENT_METHOD_BANK_TRANSFER = 'bank_transfer'

    PAYMENT_METHOD_CHOICES = [
        (PAYMENT_METHOD_CASH, 'Cash'),
        (PAYMENT_METHOD_CREDIT_CARD, 'Credit Card'),
        (PAYMENT_METHOD_DEBIT_CARD, 'Debit Card'),
        (PAYMENT_METHOD_BANK_TRANSFER, 'Bank Transfer'),
    ]

    booking = models.ForeignKey(Booking, on_delete=models.CASCADE, related_name='payment_booking')
    amount = models.DecimalField(max_digits=15, decimal_places=2, null=True)
    payment_date = models.DateField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHOD_CHOICES, default=PAYMENT_METHOD_CASH)

    def save(self, *args, **kwargs):
        if self.amount <= 0:
            raise ValueError("Payment amount must be positive.")
        if self.amount > self.booking.total_price - self.booking.get_total_paid():
            raise ValueError("Payment amount exceeds the outstanding balance for this booking.")
        super().save(*args, **kwargs)