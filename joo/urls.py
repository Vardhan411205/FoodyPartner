from django.urls import path
from . import views
from django.conf import settings
from django.conf.urls.static import static

app_name = 'joo'  # Single namespace for all URLs

urlpatterns = [
    # Partner URLs
    path('partner/', views.partner, name='partner'),
    path('partner/register/delivery/', views.delivery, name='delivery'),
    path('partner/register/restaurant/', views.restaurant, name='restaurant'),
    path('partner/register/venue/', views.venue, name='venue'),
    path('partner/register/delivery/submit/', views.register_delivery_partner, name='register_delivery_partner'),
    path('partner/register/restaurant/submit/', views.register_restaurant_partner, name='register_restaurant_partner'),
    path('partner/register/venue/submit/', views.register_venue_partner, name='register_venue_partner'),
    path('partner/restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('partner/venue/dashboard/', views.venue_dashboard, name='venue_dashboard'),
    path('partner/delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('partner/restaurant/logout/', views.restaurant_logout, name='restaurant_logout'),
    path('partner/restaurant/edit-profile/', views.update_restaurant_profile, name='update_restaurant_profile'),
    path('partner/restaurant/food-items/', views.restaurant_food_items, name='restaurant_food_items'),
    path('partner/restaurant/dining-tables/', views.restaurant_dining_tables, name='restaurant_dining_tables'),
    path('partner/restaurant/booking-history/', views.restaurant_booking_history, name='restaurant_booking_history'),
    path('partner/restaurant/update-booking-status/', views.update_booking_status, name='update_booking_status'),
    path('partner/venue/edit-profile/', views.venue_edit_profile, name='venue_edit_profile'),
    path('partner/venue/packages/', views.venue_packages, name='venue_packages'),
    path('partner/venue/events/', views.venue_events, name='venue_events'),
    path('partner/venue/update-event-status/', views.update_event_status, name='update_event_status'),
    path('partner/venue/bookings/', views.venue_bookings, name='venue_bookings'),
    path('partner/venue/logout/', views.venue_logout, name='venue_logout'),
    path('delivery/edit-profile/', views.delivery_edit_profile, name='delivery_edit_profile'),
    path('delivery/logout/', views.delivery_logout, name='delivery_logout'),
    
    # OTP verification paths
    path('verify-otp/', views.verify_otp_view, name='verify_otp'),
    path('send-otp/', views.send_otp_view, name='send_otp'),
    path('terms-conditions/', views.terms_conditions, name='terms_conditions'),

    # Partner Login URLs
    path('partner/login/', views.partner_login, name='partner_login'),
    path('partner/login/delivery/', views.delivery_login, name='delivery_login'),
    path('partner/login/restaurant/', views.restaurant_login, name='restaurant_login'),
    path('partner/login/venue/', views.venue_login, name='venue_login'),
    
    # Password Reset URLs
    path('partner/forgot-password/', views.forgot_password, name='forgot_password'),
    path('partner/verify-reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('partner/reset-password/', views.reset_password, name='reset_password'),

    # Partner Dashboard URLs
    path('partner/delivery/dashboard/', views.delivery_dashboard, name='delivery_dashboard'),
    path('partner/restaurant/dashboard/', views.restaurant_dashboard, name='restaurant_dashboard'),
    path('partner/venue/dashboard/', views.venue_dashboard, name='venue_dashboard'),

    # Partner Logout URLs
    path('partner/delivery/logout/', views.delivery_logout, name='delivery_logout'),
    path('partner/restaurant/logout/', views.restaurant_logout, name='restaurant_logout'),
    path('partner/venue/logout/', views.venue_logout, name='venue_logout'),

    # Delivery Partner URLs
    path('partner/delivery/orders/', views.delivery_orders, name='delivery_orders'),
    path('partner/delivery/complete-order/', views.complete_order, name='complete_order'),

    # New password reset paths
    path('partner/send-reset-otp/', views.send_reset_otp, name='send_reset_otp'),
    path('partner/verify-reset-otp/', views.verify_reset_otp, name='verify_reset_otp'),
    path('partner/update-password/', views.update_password, name='update_password'),
] + static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)