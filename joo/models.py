from django.db import models
from django.utils import timezone
from django.core.validators import MinValueValidator, MaxValueValidator
from decimal import Decimal

class DeliveryPartner(models.Model):
    VEHICLE_CHOICES = [
        ('bike', 'Bike'),
        ('scooter', 'Scooter'),
        ('cycle', 'Cycle'),
        ('auto', 'Auto'),
    ]

    HOURS_CHOICES = [
        ('morning', '6 AM - 12 PM'),
        ('afternoon', '12 PM - 6 PM'),
        ('evening', '6 PM - 12 AM'),
        ('night', '12 AM - 6 AM'),
        ('flexible', 'Flexible'),
    ]

    AREA_CHOICES = [
        ('north', 'North'),
        ('south', 'South'),
        ('east', 'East'),
        ('west', 'West'),
        ('central', 'Central'),
        ('all', 'All Areas'),
    ]

    full_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    address = models.TextField()
    vehicle_type = models.CharField(max_length=50, choices=VEHICLE_CHOICES, default='bike')
    vehicle_number = models.CharField(max_length=20)
    license_number = models.CharField(max_length=50)
    preferred_hours = models.CharField(max_length=100, choices=HOURS_CHOICES, default='flexible')
    preferred_area = models.CharField(max_length=100, choices=AREA_CHOICES, default='all')
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'joo_deliverypartner'

    def __str__(self):
        return self.full_name

class RestaurantPartner(models.Model):
    restaurant_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    cuisine_type = models.CharField(max_length=50)
    address = models.TextField()
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)
    restaurant_image = models.URLField(max_length=500, null=True, blank=True)

    class Meta:
        db_table = 'joo_restaurantpartner'

    def __str__(self):
        return self.restaurant_name

class VenuePartner(models.Model):
    venue_name = models.CharField(max_length=100)
    owner_name = models.CharField(max_length=100)
    email = models.EmailField(unique=True)
    phone = models.CharField(max_length=15)
    venue_type = models.CharField(max_length=50)
    seating_capacity = models.IntegerField()
    address = models.TextField()
    venue_image = models.URLField(blank=True)
    password = models.CharField(max_length=128)
    created_at = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'joo_venuepartner'

    def __str__(self):
        return self.venue_name

class OTPVerification(models.Model):
    email = models.EmailField()
    otp = models.CharField(max_length=6)
    purpose = models.CharField(max_length=20)  # For different types of verification
    created_at = models.DateTimeField(auto_now_add=True)
    is_verified = models.BooleanField(default=False)
    
    class Meta:
        db_table = 'joo_otpverification'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.email} - {self.purpose} - {self.created_at}"

class FoodItem(models.Model):
    restaurant = models.ForeignKey(RestaurantPartner, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.CharField(max_length=50)
    image_url = models.URLField(max_length=500, blank=True, null=True)
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0)
    is_available = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['category', 'name']

    def __str__(self):
        return f"{self.name} - {self.restaurant.restaurant_name}"

class DiningTable(models.Model):
    STATUS_CHOICES = [
        ('available', 'Available'),
        ('occupied', 'Occupied'),
        ('reserved', 'Reserved'),
    ]
    
    CATEGORY_CHOICES = [
        ('luxury', 'Luxury'),
        ('premium', 'Premium'),
        ('casual', 'Casual'),
        ('budget', 'Budget'),
    ]
    
    restaurant = models.ForeignKey(RestaurantPartner, on_delete=models.CASCADE)
    table_number = models.CharField(max_length=20)
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='casual')
    seating_capacity = models.IntegerField(
        validators=[MinValueValidator(2), MaxValueValidator(20)],
        default=4
    )
    price = models.DecimalField(
        max_digits=10, 
        decimal_places=2,
        default=500.00
    )
    rating = models.DecimalField(
        max_digits=3, 
        decimal_places=1, 
        default=5.0
    )
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='available')
    image_url = models.URLField(default='https://via.placeholder.com/300')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Table {self.table_number} - {self.restaurant.restaurant_name}"

    class Meta:
        ordering = ['table_number']

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    restaurant = models.ForeignKey(RestaurantPartner, on_delete=models.CASCADE)
    table = models.ForeignKey(DiningTable, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    guest_count = models.IntegerField()
    booking_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Booking for {self.customer_name} at {self.restaurant.restaurant_name}"

class Event(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    venue = models.ForeignKey(VenuePartner, on_delete=models.CASCADE)
    customer_name = models.CharField(max_length=100)
    customer_phone = models.CharField(max_length=20)
    event_type = models.CharField(max_length=50)
    event_date = models.DateTimeField()
    guest_count = models.IntegerField()
    package = models.ForeignKey('EventPackage', on_delete=models.SET_NULL, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    rating = models.DecimalField(max_digits=3, decimal_places=1, null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.event_type} at {self.venue.venue_name} on {self.event_date}"

class EventPackage(models.Model):
    venue = models.ForeignKey(VenuePartner, on_delete=models.CASCADE)
    name = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    max_guests = models.IntegerField()
    duration_hours = models.IntegerField()
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.venue.venue_name}"

class Order(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed')
    )
    
    order_id = models.CharField(max_length=10, unique=True)
    customer_email = models.EmailField()
    delivery_partner = models.ForeignKey(DeliveryPartner, on_delete=models.CASCADE)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Order #{self.order_id}"

class VenueBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    
    order_id = models.CharField(max_length=50, unique=True)
    customer_email = models.EmailField()
    venue_email = models.EmailField(default='')
    booking_date = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    venue = models.ForeignKey(VenuePartner, on_delete=models.CASCADE)
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(default=timezone.now)

    def __str__(self):
        return f"Booking {self.order_id} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.venue_email and self.venue:
            self.venue_email = self.venue.email
        if not self.pk:
            self.created_at = timezone.now()
        self.updated_at = timezone.now()
        super().save(*args, **kwargs)

class RestaurantBooking(models.Model):
    STATUS_CHOICES = (
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled')
    )
    
    order_id = models.CharField(max_length=50, unique=True)
    customer_email = models.EmailField()
    restaurant_email = models.EmailField(default='')
    booking_date = models.DateTimeField()
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    restaurant = models.ForeignKey(RestaurantPartner, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-booking_date']

    def __str__(self):
        return f"Booking {self.order_id} - {self.status}"

    def save(self, *args, **kwargs):
        if not self.restaurant_email and self.restaurant:
            self.restaurant_email = self.restaurant.email
        super().save(*args, **kwargs)

class ResetPassword(models.Model):
    PARTNER_CHOICES = (
        ('restaurant', 'Restaurant Partner'),
        ('venue', 'Venue Partner'),
        ('delivery', 'Delivery Partner')
    )
    
    email = models.EmailField()
    partner_type = models.CharField(max_length=20, choices=PARTNER_CHOICES)
    otp = models.CharField(max_length=6)
    is_verified = models.BooleanField(default=False)
    created_at = models.DateTimeField(default=timezone.now)
    expires_at = models.DateTimeField()

    def __str__(self):
        return f"Reset password for {self.email} ({self.partner_type})"

    def save(self, *args, **kwargs):
        if not self.pk:
            # Set expiry to 10 minutes from creation
            self.expires_at = timezone.now() + timezone.timedelta(minutes=10)
        super().save(*args, **kwargs)

    @property
    def is_expired(self):
        return timezone.now() > self.expires_at
