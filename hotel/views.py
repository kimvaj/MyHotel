from rest_framework import viewsets, status,permissions
from django.db import IntegrityError
from datetime import timedelta
from rest_framework.response import Response
from django.utils import timezone
from rest_framework.reverse import reverse
from .serializers import HotelSerializer
from rest_framework.response import Response
from rest_framework.views import APIView
from hotel.models import Hotel
from rest_framework import viewsets
from rest_framework.response import Response
from rest_framework.exceptions import ValidationError
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from .models import Hotel, Staff, Guest, RoomType, Room, Booking, Payment
from .serializers import (
    HotelSerializer, StaffSerializer, GuestSerializer,
    RoomTypeSerializer, RoomSerializer, BookingSerializer, PaymentSerializer
)
from rest_framework.decorators import action
from drf_yasg.utils import swagger_auto_schema
from django.http import Http404

    
    
class SoftDeleteViewSetMixin(viewsets.ModelViewSet):
    def get_object(self):
        queryset = self.filter_queryset(self.get_queryset())
        filter_kwargs = {self.lookup_field: self.kwargs[self.lookup_field]}
        obj = queryset.filter(**filter_kwargs).first()
        if not obj:
            queryset = self.get_queryset().model.all_objects
            obj = queryset.filter(**filter_kwargs).first()
        if not obj:
            raise Http404
        self.check_object_permissions(self.request, obj)
        return obj

    def destroy(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(detail=True, methods=['post'])
    def restore(self, request, pk=None):
        instance = self.get_object()
        instance.restore()
        return Response(status=status.HTTP_200_OK)

    @action(detail=True, methods=['delete'])
    def hard_delete(self, request, pk=None):
        instance = self.get_object()
        instance.hard_delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


    
    
class HotelViewSet(SoftDeleteViewSetMixin):
    queryset = Hotel.objects.all()
    serializer_class = HotelSerializer
    # permission_classes = [IsAuthenticated]
    


class StaffViewSet(SoftDeleteViewSetMixin):
    queryset = Staff.objects.all()
    serializer_class = StaffSerializer
    # permission_classes = [IsAuthenticated]

class GuestViewSet(SoftDeleteViewSetMixin):
    queryset = Guest.all_objects.all()
    serializer_class = GuestSerializer


    

class RoomTypeViewSet(SoftDeleteViewSetMixin):
    queryset = RoomType.objects.all()
    serializer_class = RoomTypeSerializer
    # permission_classes = [IsAuthenticated]

class RoomViewSet(SoftDeleteViewSetMixin):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        try:
            serializer.is_valid(raise_exception=True)
            self.perform_create(serializer)
        except ValidationError as e:
            return Response({'error': e.detail}, status=status.HTTP_400_BAD_REQUEST)
        except IntegrityError as e:
            if 'duplicate key value violates unique constraint' in str(e):
                return Response({'error': 'Room with this room number already exists.'}, status=status.HTTP_400_BAD_REQUEST)
            else:
                return Response({'error': str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        headers = self.get_success_headers(serializer.data)
        return Response(serializer.data, status=status.HTTP_201_CREATED, headers=headers)

# class BookingViewSet(viewsets.ModelViewSet):
#     queryset = Booking.objects.all()
#     serializer_class = BookingSerializer

#     def perform_create(self, serializer):
#         room = serializer.validated_data['room']
#         if room.status == Room.OCCUPIED:
#             raise ValidationError("The room is already occupied.")
#         room.status = Room.OCCUPIED
#         room.save()
#         serializer.save()

#     def perform_destroy(self, instance):
#         room = instance.room
#         room.status = Room.AVAILABLE
#         room.save()
#         instance.delete()

#     def calculate_total_price(self, booking):
#         price_per_night = booking.room.room_type.price_per_night
#         total_nights = (booking.check_out_date - booking.check_in_date).days
#         return total_nights * price_per_night

# class BookingViewSet(viewsets.ModelViewSet):
#     queryset = Booking.objects.all()
#     serializer_class = BookingSerializer

#     def perform_create(self, serializer):
#         room = serializer.validated_data['room']
#         if room.status == Room.OCCUPIED:
#             raise ValidationError("The room is already occupied.")
#         room.status = Room.OCCUPIED
#         room.save()
#         serializer.save()

#     def perform_destroy(self, instance):
#         room = instance.room
#         room.status = Room.AVAILABLE
#         room.save()
#         instance.delete()

#     def calculate_total_price(self, booking):
#         price_per_night = booking.room.room_type.price_per_night
#         total_nights = (booking.check_out_date - booking.check_in_date).days
#         return total_nights * price_per_night

class BookingViewSet(SoftDeleteViewSetMixin):
    queryset = Booking.objects.all()
    serializer_class = BookingSerializer

    def perform_create(self, serializer):
        room = serializer.validated_data['room']
        if room.status == Room.OCCUPIED:
            raise ValidationError("The room is already occupied.")
        room.status = Room.OCCUPIED
        room.save()
        booking = serializer.save()
        booking.total_price = self.calculate_total_price(booking)
        booking.save()

    def perform_destroy(self, instance):
        room = instance.room
        room.status = Room.AVAILABLE
        room.save()
        instance.delete()

    def calculate_total_price(self, booking):
        price_per_night = booking.room.room_type.price_per_night
        total_nights = (booking.check_out_date - booking.check_in_date).days
        return total_nights * price_per_night






class PaymentViewSet(SoftDeleteViewSetMixin):
    queryset = Payment.objects.all()
    serializer_class = PaymentSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        booking = serializer.validated_data['booking']
        
        # Calculate the amount based on the outstanding balance of the booking
        amount = booking.total_price - booking.get_total_paid()
        
        # Ensure the amount is positive
        if amount <= 0:
            return Response({"detail": "Payment amount must be positive."}, status=status.HTTP_400_BAD_REQUEST)
        
        # Set the payment date to the current date and time
        payment_date = timezone.now()
        
        # Create the Payment instance directly without passing amount through serializer
        payment = Payment.objects.create(
            booking=booking,
            amount=amount,
            payment_date=payment_date,
            payment_method=serializer.validated_data['payment_method']  # Assuming payment_method is provided in the request
        )










class APIRootView(APIView):
    def get(self, request, format=None):
        return Response(
            {
                'auth': {
                    "login": reverse('token_obtain_pair', request=request, format=format),
                    "refresh_token": reverse('token_refresh', request=request, format=format),
                    "register": reverse('register', request=request, format=format),
                    "login": reverse('login', request=request, format=format),
                    "logout": reverse('logout', request=request, format=format),
                },
                "users": reverse("user-list", request=request, format=format),
                "groups": reverse("group-list", request=request, format=format),
                "permissions": reverse("permission-list", request=request, format=format),
                "hotels": reverse("hotel-list", request=request, format=format),
                "staffs": reverse("staff-list", request=request, format=format),
                "guests": reverse("guest-list", request=request, format=format),
                "roomtypes": reverse("roomtype-list", request=request, format=format),
                "rooms": reverse("room-list", request=request, format=format),
                'bookings': reverse("booking-list", request=request, format=format),
                "payments": reverse("payment-list", request=request, format=format),
                
            }
        )