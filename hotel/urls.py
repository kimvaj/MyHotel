from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
    TokenVerifyView,
)
from django.urls import path, include
from rest_framework import routers
from account.views import register_user, user_login, user_logout
from account.views import UserViewSet, GroupViewSet, PermissionViewSet
from hotel.views import HotelViewSet, StaffViewSet, GuestViewSet, RoomTypeViewSet, RoomViewSet, PaymentViewSet, BookingViewSet
from . import views


router = routers.DefaultRouter()
router.register(r'users', UserViewSet)
router.register(r'groups', GroupViewSet)
router.register(r'permissions', PermissionViewSet)
router.register(r'hotels', HotelViewSet)
router.register(r'staffs', StaffViewSet)
router.register(r'guests', GuestViewSet)
router.register(r'roomtypes', RoomTypeViewSet)
router.register(r'rooms', RoomViewSet)
router.register(r'bookings', BookingViewSet)
router.register(r'payments', PaymentViewSet)
urlpatterns = [
    path('', views.APIRootView.as_view(), name='api-root'),
    path('', include(router.urls)),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('token/verify/', TokenVerifyView.as_view(), name='token_verify'),
    path('register/', register_user, name='register'),
    path('login/', user_login, name='login'),
    path('logout/', user_logout, name='logout'),
]

