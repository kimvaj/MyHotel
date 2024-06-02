# hotel/tasks.py

from celery import shared_task
from django.utils import timezone
from hotel.models import Booking, Room
from datetime import date


@shared_task
def update_room_status():
    test_date = date(2024, 6, 30)  # Simulate 30/6/2024
    bookings = Booking.objects.filter(
        check_out_date__lt=test_date, room__status=Room.OCCUPIED
    )
    for booking in bookings:
        room = booking.room
        room.status = Room.AVAILABLE
        room.save()
