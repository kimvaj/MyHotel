from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from datetime import timedelta
from .models import Hotel, Staff, Guest, RoomType, Room, Booking, Payment


class HotelSerializer(serializers.ModelSerializer):
    class Meta:
        model = Hotel
        fields = '__all__'

class StaffSerializer(serializers.ModelSerializer):
    hotel = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
    
    class Meta:
        model = Staff
        fields = '__all__'

class GuestSerializer(serializers.ModelSerializer):
    class Meta:
        model = Guest
        fields = '__all__'

class RoomTypeSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoomType
        fields = '__all__'

class RoomSerializer(serializers.ModelSerializer):
    hotel = serializers.PrimaryKeyRelatedField(queryset=Hotel.objects.all())
    room_type = serializers.PrimaryKeyRelatedField(queryset=RoomType.objects.all())
    
    class Meta:
        model = Room
        fields = '__all__'

    def validate(self, data):
        # Ensure room number is unique within the same hotel
        if Room.objects.filter(hotel=data['hotel'], room_number=data['room_number']).exists():
            raise serializers.ValidationError("A room with this number already exists in this hotel.")
        return data


# class BookingSerializer(serializers.ModelSerializer):
#     number_of_days = serializers.SerializerMethodField()

#     class Meta:
#         model = Booking
#         fields = ['id', 'guest', 'room', 'check_in_date', 'check_out_date', 'number_of_days', 'total_price']
#         read_only_fields = ['total_price', 'number_of_days']

#     def get_number_of_days(self, obj):
#         if obj.check_in_date and obj.check_out_date:
#             return (obj.check_out_date - obj.check_in_date).days
#         return None

#     def validate(self, data):
#         check_in_date = data.get('check_in_date')
#         check_out_date = data.get('check_out_date')
#         number_of_days = data.get('number_of_days')
        
#         if check_in_date and check_out_date:
#             if check_in_date >= check_out_date:
#                 raise serializers.ValidationError("Check-in date must be before check-out date.")
#         elif check_in_date and number_of_days:
#             if number_of_days <= 0:
#                 raise serializers.ValidationError("Number of days must be greater than 0.")
#             data['check_out_date'] = check_in_date + timedelta(days=number_of_days)
#         else:
#             raise serializers.ValidationError("Either check-in and check-out dates or check-in date and number of days must be provided.")
        
#         return data

#     def create(self, validated_data):
#         number_of_days = validated_data.pop('number_of_days', None)
#         check_in_date = validated_data['check_in_date']
        
#         if number_of_days:
#             validated_data['check_out_date'] = check_in_date + timedelta(days=number_of_days)
            
#         return super().create(validated_data)

# class BookingSerializer(serializers.ModelSerializer):
#     number_of_days = serializers.IntegerField(write_only=True, required=True, help_text="Number of days to stay")
#     check_out_date = serializers.DateField(read_only=True)

#     class Meta:
#         model = Booking
#         fields = ['id', 'guest', 'room', 'check_in_date', 'check_out_date', 'number_of_days', 'total_price']
#         read_only_fields = ['total_price', 'check_out_date']

#     def validate(self, data):
#         check_in_date = data.get('check_in_date')
#         number_of_days = data.get('number_of_days')

#         if not check_in_date:
#             raise serializers.ValidationError("Check-in date must be provided.")
#         if number_of_days <= 0:
#             raise serializers.ValidationError("Number of days must be greater than 0.")
        
#         return data

#     def create(self, validated_data):
#         number_of_days = validated_data.pop('number_of_days')
#         check_in_date = validated_data['check_in_date']
#         validated_data['check_out_date'] = check_in_date + timedelta(days=number_of_days)

#         return super().create(validated_data)
class BookingSerializer(serializers.ModelSerializer):
    number_of_days = serializers.IntegerField(required=False, write_only=True, help_text="Number of days to stay")

    class Meta:
        model = Booking
        fields = ['id', 'guest', 'room', 'check_in_date', 'check_out_date', 'number_of_days', 'total_price']
        read_only_fields = ['total_price']

    def validate(self, data):
        check_in_date = data.get('check_in_date')
        check_out_date = data.get('check_out_date')
        number_of_days = data.get('number_of_days')

        if number_of_days is not None:
            # If number_of_days is provided, calculate check_out_date
            if check_out_date:
                raise serializers.ValidationError("Do not provide check_out_date when number_of_days is provided.")
            # Calculate check_out_date based on check_in_date and number_of_days
            data['check_out_date'] = check_in_date + timedelta(days=number_of_days)
        elif not check_out_date:
            raise serializers.ValidationError("Either check_out_date or number_of_days must be provided.")

        if check_in_date and check_out_date:
            if check_in_date >= check_out_date:
                raise serializers.ValidationError("Check-in date must be before check-out date.")

        return data

    def create(self, validated_data):
        return super().create(validated_data)

    def update(self, instance, validated_data):
        return super().update(instance, validated_data)

    def to_representation(self, instance):
        representation = super().to_representation(instance)
        if 'check_in_date' in representation and 'check_out_date' in representation:
            check_in_date = instance.check_in_date
            check_out_date = instance.check_out_date
            representation['number_of_days'] = (check_out_date - check_in_date).days
        return representation















class PaymentSerializer(serializers.ModelSerializer):
    booking = serializers.PrimaryKeyRelatedField(queryset=Booking.objects.all())
    amount = serializers.DecimalField(read_only=True, max_digits=9, decimal_places=2)
    payment_date = serializers.DateField(read_only=True)
    is_deleted = serializers.BooleanField(read_only=True)  # Add read-only field for is_deleted

    class Meta:
        model = Payment
        fields = ['id', 'booking', 'amount', 'payment_date', 'payment_method', 'is_deleted']

    def validate(self, data):
        booking = data.get('booking')
        
        if booking is None:
            raise serializers.ValidationError("Booking must be provided.")
        
        return data
