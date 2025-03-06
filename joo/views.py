from django.shortcuts import render, redirect
from django.http import HttpResponse, JsonResponse
from django.contrib import messages
from django.contrib.auth.decorators import login_required
import random
import json
from django.views.decorators.csrf import csrf_exempt
from django.urls import reverse
from django.core.files.storage import FileSystemStorage
from django.db.models import Sum, Avg
from django.utils import timezone
from datetime import timedelta
import hashlib
from django.core.mail import send_mail
from django.conf import settings
from functools import wraps
from django.db import connection
from django.contrib.auth import login
import os
from django.contrib.auth.hashers import make_password
from django.db import transaction
from django.db import connections
import psycopg2
from decimal import Decimal

from .models import (
    DeliveryPartner, 
    RestaurantPartner, 
    VenuePartner, 
    OTPVerification,
    FoodItem, 
    DiningTable, 
    Booking, 
    Event, 
    EventPackage,
    Order,
    ResetPassword
)

from .otp_handler import send_otp, verify_otp, is_email_verified
from .food_items import FoodItemManager
from .decorators import restaurant_required

# Create your views here.

# User view
def user(request):
    """
    View for user login page
    URL: /user/
    Template: login/user.html
    """
    try:
        return render(request, 'login/user.html')
    except Exception as e:
        messages.error(request, f"Error loading user page: {str(e)}")
        return redirect('joo:partner')

# Partner main page
def partner(request):
    """Display partner landing page"""
    return render(request, 'login/partner.html')

# Login views
@csrf_exempt
def delivery_login(request):
    """Handle delivery partner login"""
    # Clear any existing invalid sessions
    if not request.session.get('delivery_id'):
        request.session.flush()
    
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            if not email or not password:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email and password are required'
                })
            
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            try:
                delivery = DeliveryPartner.objects.get(
                    email=email,
                    password=hashed_password,
                    is_active=True
                )
                
                # Store delivery info in session
                request.session['delivery_id'] = delivery.id
                request.session['delivery_name'] = delivery.full_name
                request.session['delivery_email'] = delivery.email
                request.session.save()
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Login successful',
                    'redirect_url': reverse('joo:delivery_dashboard')
                })
                
            except DeliveryPartner.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid email or password'
                })
            
        except Exception as e:
            print(f"Login error: {str(e)}")
            return JsonResponse({
                'status': 'error',
                'message': 'Error during login. Please try again.'
            })

    # For GET requests, render the login page
    return render(request, 'login/partner/login/delivery_login.html')

@csrf_exempt
def restaurant_login(request):
    """Handle restaurant partner login"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Hash the provided password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Try to find the restaurant partner
            restaurant = RestaurantPartner.objects.get(
                email=email,
                password=hashed_password,
                is_active=True
            )
            
            # Store restaurant info in session
            request.session['restaurant_id'] = restaurant.id
            request.session['restaurant_name'] = restaurant.restaurant_name
            request.session['restaurant_email'] = restaurant.email
            
            return JsonResponse({
                'status': 'success',
                'message': 'Login successful',
                'redirect_url': reverse('joo:restaurant_dashboard')
            })
            
        except RestaurantPartner.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid email or password'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return render(request, 'login/partner/login/restaurant_login.html')

@csrf_exempt
def venue_login(request):
    """Handle venue partner login"""
    if request.method == 'POST':
        try:
            email = request.POST.get('email')
            password = request.POST.get('password')
            
            # Hash the provided password
            hashed_password = hashlib.sha256(password.encode()).hexdigest()
            
            # Try to find the venue partner
            venue = VenuePartner.objects.get(
                email=email,
                password=hashed_password,
                is_active=True
            )
            
            # Store venue info in session
            request.session['venue_id'] = venue.id
            request.session['venue_name'] = venue.venue_name
            request.session['venue_email'] = venue.email
            
            return JsonResponse({
                'status': 'success',
                'message': 'Login successful',
                'redirect_url': reverse('joo:venue_dashboard')
            })
            
        except VenuePartner.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid email or password'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return render(request, 'login/partner/login/venue_login.html')

# Registration views
def delivery(request):
    """Display delivery partner registration"""
    return render(request, 'login/partner/register/delivery.html')

def restaurant(request):
    """Display restaurant partner registration"""
    return render(request, 'login/partner/register/restaurant.html')

def venue(request):
    """Display venue partner registration"""
    return render(request, 'login/partner/register/venue.html')

@csrf_exempt
def send_otp_view(request):
    """Handle OTP sending"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            # Get the referer URL to determine registration type
            referer = request.META.get('HTTP_REFERER', '')
            
            # Determine purpose based on URL
            if 'delivery' in referer:
                purpose = 'delivery'
            elif 'restaurant' in referer:
                purpose = 'restaurant'
            elif 'venue' in referer:
                purpose = 'venue'
            else:
                purpose = 'signup'
            
            if not email:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email is required'
                })
            
            result = send_otp(email, purpose)
            return JsonResponse(result)
                
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def verify_otp_view(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            otp = data.get('otp')
            
            # Get the referer URL to determine the registration type
            referer = request.META.get('HTTP_REFERER', '')
            
            # Determine purpose based on URL
            if 'delivery' in referer:
                purpose = 'delivery'
            elif 'restaurant' in referer:
                purpose = 'restaurant'
            elif 'venue' in referer:
                purpose = 'venue'
            else:
                purpose = 'signup'
            
            if verify_otp(email, otp, purpose):
                return JsonResponse({
                    'status': 'success',
                    'message': 'OTP verified successfully'
                })
            else:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid OTP'
                })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

@csrf_exempt
def register_delivery_partner(request):
    """Handle delivery partner registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            # Check if email is verified with purpose='delivery'
            if not is_email_verified(email=email, purpose='delivery'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please verify your email first'
                })

            # Check if delivery partner already exists
            if DeliveryPartner.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already registered'
                })

            # Hash the password
            password = data.get('password')
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Create delivery partner
            delivery_partner = DeliveryPartner.objects.create(
                full_name=data.get('full_name'),
                email=email,
                phone=data.get('phone'),
                address=data.get('address'),
                vehicle_type=data.get('vehicle_type'),
                vehicle_number=data.get('vehicle_number'),
                license_number=data.get('license_number'),
                preferred_hours=data.get('preferred_hours'),
                preferred_area=data.get('preferred_area'),
                password=hashed_password,
                is_active=True
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Registration successful',
                'redirect_url': reverse('joo:delivery_login')
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def register_restaurant_partner(request):
    """Handle restaurant partner registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            email = data.get('email')
            
            # Check if email is verified with purpose='restaurant'
            if not is_email_verified(email=email, purpose='restaurant'):
                return JsonResponse({
                    'status': 'error',
                    'message': 'Please verify your email first'
                })

            # Check if restaurant already exists
            if RestaurantPartner.objects.filter(email=email).exists():
                return JsonResponse({
                    'status': 'error',
                    'message': 'Email already registered'
                })

            # Hash the password
            password = data.get('password')
            hashed_password = hashlib.sha256(password.encode()).hexdigest()

            # Create restaurant partner
            restaurant = RestaurantPartner.objects.create(
                restaurant_name=data.get('restaurant_name'),
                owner_name=data.get('owner_name'),
                email=email,
                phone=data.get('phone'),
                cuisine_type=data.get('cuisine_type'),
                address=data.get('address'),
                restaurant_image=data.get('restaurant_image'),
                password=hashed_password,
                is_active=True
            )

            return JsonResponse({
                'status': 'success',
                'message': 'Registration successful',
                'redirect_url': reverse('joo:restaurant_login')
            })

        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def register_venue_partner(request):
    """Handle venue partner registration"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            # Get all the fields from the request
            venue_name = data.get('venue_name')
            owner_name = data.get('owner_name')
            email = data.get('email')
            phone = data.get('phone')
            venue_type = data.get('venue_type')
            seating_capacity = data.get('seating_capacity')
            price = data.get('price', 0.00)
            address = data.get('address')
            venue_image = data.get('venue_image')
            password = data.get('password')

            # Validate required fields
            if not all([venue_name, owner_name, email, phone, venue_type, 
                       seating_capacity, price, address, password]):
                return JsonResponse({
                    'status': 'error',
                    'message': 'All fields are required'
                })

            # Create new venue partner
            venue_partner = VenuePartner(
                venue_name=venue_name,
                owner_name=owner_name,
                email=email,
                phone=phone,
                venue_type=venue_type,
                seating_capacity=seating_capacity,
                price=Decimal(str(price)),
                address=address,
                venue_image=venue_image
            )
            # Hash and set the password
            venue_partner.set_password(password)
            venue_partner.save()

            return JsonResponse({
                'status': 'success',
                'message': 'Registration successful'
            })

        except json.JSONDecodeError:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid JSON data'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })

    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def forgot_password(request):
    """Handle partner forgot password"""
    return render(request, 'login/partner/login/forgot_password.html')

@csrf_exempt
def verify_reset_otp(request):
    """Handle partner OTP verification"""
    return render(request, 'login/partner/login/verify_reset_otp.html')

@csrf_exempt
def reset_password(request):
    """Handle partner password reset"""
    return render(request, 'login/partner/login/reset_password.html')

def terms_conditions(request):
    """Display terms and conditions page"""
    return render(request, 'login/terms_conditions.html')

@csrf_exempt
def restaurant_dashboard(request):
    print("Entering dashboard view")  # Debug print
    """Display restaurant partner dashboard"""
    # Check if restaurant is logged in
    if 'restaurant_id' not in request.session:
        messages.error(request, "Please login first")
        return redirect('joo:restaurant_login')
    
    try:
        restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
        return render(request, 'partner/restaurant/restaurant_dashboard.html', {
            'restaurant': restaurant
        })
    except RestaurantPartner.DoesNotExist:
        messages.error(request, "Restaurant not found")
        return redirect('joo:restaurant_login')

def venue_login_required(view_func):
    @wraps(view_func)
    def wrapper(request, *args, **kwargs):
        if 'venue_id' not in request.session:
            return redirect('joo:venue_login')
        return view_func(request, *args, **kwargs)
    return wrapper

@venue_login_required
def venue_dashboard(request):
    """Display venue partner dashboard"""
    if 'venue_id' not in request.session:
        messages.error(request, "Please login first")
        return redirect('joo:venue_login')
    
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        
        # Get some basic stats
        total_events = Event.objects.filter(venue=venue).count()
        upcoming_events = Event.objects.filter(
            venue=venue,
            event_date__gte=timezone.now()
        ).count()
        active_packages = EventPackage.objects.filter(
            venue=venue,
            is_active=True
        ).count()
        
        context = {
            'venue': venue,
            'total_events': total_events,
            'upcoming_events': upcoming_events,
            'active_packages': active_packages
        }
        
        return render(request, 'partner/venue/venue_dashboard.html', context)
        
    except VenuePartner.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('joo:venue_login')
    except Exception as e:
        print(f"Error in venue_dashboard: {str(e)}")
        return render(request, 'partner/venue/venue_dashboard.html', {
            'venue': None,
            'error_message': 'An error occurred loading the dashboard'
        })

def delivery_dashboard(request):
    """Display delivery partner dashboard"""
    delivery_id = request.session.get('delivery_id')
    
    if not delivery_id:
        messages.error(request, "Please login first")
        return redirect('joo:delivery_login')
        
    try:
        delivery = DeliveryPartner.objects.get(id=delivery_id)
        context = {
            'delivery': delivery,
            'todays_deliveries': 0,
            'todays_earnings': 0,
            'rating': 4.5,
            'active_hours': 0
        }
        return render(request, 'partner/delivery/delivery_dashboard.html', context)
        
    except DeliveryPartner.DoesNotExist:
        request.session.flush()
        messages.error(request, "Delivery partner not found")
        return redirect('joo:delivery_login')

def logout(request):
    # Clear all session data
    request.session.flush()
    return redirect('joo:partner')

@csrf_exempt
def restaurant_logout(request):
    """Handle restaurant partner logout"""
    keys_to_remove = [
        'restaurant_id',
        'restaurant_name',
        'restaurant_email'
    ]
    
    for key in keys_to_remove:
        request.session.pop(key, None)
    
    request.session.flush()
    return redirect('joo:restaurant_login')

@csrf_exempt
def venue_logout(request):
    """Handle venue partner logout"""
    keys_to_remove = [
        'venue_id',
        'venue_name',
        'venue_email'
    ]
    
    for key in keys_to_remove:
        request.session.pop(key, None)
    
    request.session.flush()
    return redirect('joo:venue_login')

@csrf_exempt
def update_restaurant_profile(request):
    """Handle restaurant profile editing"""
    if 'restaurant_id' not in request.session:
        return redirect('joo:restaurant_login')
    
    try:
        with transaction.atomic():
            restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
            
            if request.method == 'POST':
                try:
                    old_name = restaurant.restaurant_name
                    # Update basic info
                    restaurant.restaurant_name = request.POST.get('restaurant_name', restaurant.restaurant_name)
                    restaurant.owner_name = request.POST.get('owner_name', restaurant.owner_name)
                    restaurant.email = request.POST.get('email', restaurant.email)
                    restaurant.phone = request.POST.get('phone', restaurant.phone)
                    restaurant.address = request.POST.get('address', restaurant.address)
                    restaurant.restaurant_image = request.POST.get('restaurant_image', restaurant.restaurant_image)
                    
                    restaurant.save()
                    
                    # Update both food items and dining tables
                    if old_name != restaurant.restaurant_name:
                        FoodItem.objects.filter(restaurant=restaurant).update(
                            restaurant_name=restaurant.restaurant_name
                        )
                        DiningTable.objects.filter(restaurant=restaurant).update(
                            restaurant_name=restaurant.restaurant_name
                        )
                    
                    # Update session data
                    request.session['restaurant_name'] = restaurant.restaurant_name
                    request.session['restaurant_image'] = restaurant.restaurant_image
                    
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Profile updated successfully'
                        })
                    else:
                        messages.success(request, 'Profile updated successfully')
                        return redirect('joo:update_restaurant_profile')
                    
                except Exception as e:
                    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                        return JsonResponse({
                            'status': 'error',
                            'message': str(e)
                        })
                    else:
                        messages.error(request, f'Error updating profile: {str(e)}')
            
        return render(request, 'partner/restaurant/edit_profile.html', {
            'restaurant': restaurant
        })
        
    except RestaurantPartner.DoesNotExist:
        messages.error(request, "Restaurant not found")
        return redirect('joo:restaurant_login')

@csrf_exempt
def restaurant_food_items(request):
    """Handle restaurant food items"""
    if 'restaurant_id' not in request.session:
        return JsonResponse({
            'status': 'error',
            'message': 'Please login to continue'
        }, status=401)
    
    try:
        restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
        
        if request.method == 'POST':
            try:
                # Parse JSON data if it's an AJAX request
                if request.headers.get('Content-Type') == 'application/json':
                    data = json.loads(request.body)
                    action = data.get('action')

                    if action == 'add':
                        # Validate required fields
                        required_fields = ['name', 'price', 'category', 'image_url']
                        for field in required_fields:
                            if not data.get(field):
                                return JsonResponse({
                                    'status': 'error',
                                    'message': f'{field.replace("_", " ").title()} is required'
                                })

                        # Create new food item
                        food_item = FoodItem.objects.create(
                            restaurant=restaurant,
                            name=data['name'],
                            restaurant_name=restaurant.restaurant_name,
                            price=data['price'],
                            category=data['category'],
                            image_url=data['image_url'],
                            rating=float(data.get('rating', 0)),
                            is_available=True
                        )

                        return JsonResponse({
                            'status': 'success',
                            'message': 'Food item added successfully',
                            'item': {
                                'id': food_item.id,
                                'name': food_item.name,
                                'price': float(food_item.price),
                                'category': food_item.category,
                                'image_url': food_item.image_url,
                                'rating': float(food_item.rating),
                                'is_available': food_item.is_available
                            }
                        })
                    elif action == 'edit':
                        # Handle edit action
                        item_id = data.get('item_id')
                        if not item_id:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Item ID is required for editing'
                            })

                        food_item = FoodItem.objects.get(id=item_id, restaurant=restaurant)
                        food_item.name = data.get('name', food_item.name)
                        food_item.price = data.get('price', food_item.price)
                        food_item.category = data.get('category', food_item.category)
                        food_item.image_url = data.get('image_url', food_item.image_url)
                        food_item.save()

                        return JsonResponse({
                            'status': 'success',
                            'message': 'Food item updated successfully'
                        })
                    elif action == 'delete':
                        # Handle delete action
                        item_id = data.get('item_id')
                        if not item_id:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Item ID is required for deletion'
                            })

                        FoodItem.objects.filter(id=item_id, restaurant=restaurant).delete()
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Food item deleted successfully'
                        })
                    else:
                        return JsonResponse({
                            'status': 'error',
                            'message': 'Invalid action'
                        })
                
            except FoodItem.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Food item not found'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        
        # Get all food items for this restaurant
        food_items = FoodItem.objects.filter(restaurant=restaurant).order_by('category', 'name')
        
        return render(request, 'partner/restaurant/food_items.html', {
            'restaurant': restaurant,
            'food_items': food_items
        })
        
    except RestaurantPartner.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Restaurant not found'
        })

@csrf_exempt
def delivery_orders(request):
    """Handle delivery partner orders view"""
    if 'delivery_id' not in request.session:
        return redirect('joo:delivery_login')
    
    try:
        delivery_partner = DeliveryPartner.objects.get(id=request.session['delivery_id'])
        
        # Connect directly to the database
        conn = psycopg2.connect(
            dbname="neondb",
            user="neondb_owner",
            password="npg_wIejAbND13TE",
            host="ep-flat-king-a181p50o-pooler.ap-southeast-1.aws.neon.tech",
            port="5432",
            sslmode="require"
        )
        
        cursor = conn.cursor()
        cursor.execute("""
            SELECT id, order_id, customer_email, restaurant_name, status 
            FROM joo_order 
            WHERE order_type = 'food' 
            ORDER BY booking_date DESC
        """)
        
        columns = [desc[0] for desc in cursor.description]
        orders = [dict(zip(columns, row)) for row in cursor.fetchall()]
        
        cursor.close()
        conn.close()
        
        return render(request, 'partner/delivery/orders.html', {
            'orders': orders
        })
        
    except DeliveryPartner.DoesNotExist:
        messages.error(request, "Delivery partner not found")
        return redirect('joo:delivery_login')
    except Exception as e:
        messages.error(request, f"Database error: {str(e)}")
        return redirect('joo:delivery_dashboard')

@csrf_exempt
def complete_order(request):
    """Handle order completion by delivery partner"""
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            
            conn = psycopg2.connect(
                dbname="neondb",
                user="neondb_owner",
                password="npg_wIejAbND13TE",
                host="ep-flat-king-a181p50o-pooler.ap-southeast-1.aws.neon.tech",
                port="5432",
                sslmode="require"
            )
            
            cursor = conn.cursor()
            
            # Check if order exists and is pending
            cursor.execute("""
                SELECT id, status 
                FROM joo_order 
                WHERE id = %s AND order_type = 'food'
            """, [data['order_id']])
            
            order = cursor.fetchone()
            
            if not order:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Order not found'
                })
            
            if order[1] != 'pending':
                return JsonResponse({
                    'status': 'error',
                    'message': 'Order is not in pending status'
                })
            
            # Update the order status
            cursor.execute("""
                UPDATE joo_order 
                SET status = 'completed', 
                    updated_at = NOW() 
                WHERE id = %s
            """, [data['order_id']])
            
            conn.commit()
            cursor.close()
            conn.close()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Order completed successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def restaurant_dining_tables(request):
    """Handle restaurant dining tables"""
    if 'restaurant_id' not in request.session or 'restaurant_name' not in request.session:
        return JsonResponse({
            'status': 'error',
            'message': 'Please login first'
        }) if request.headers.get('Content-Type') == 'application/json' else redirect('joo:restaurant_login')
    
    try:
        restaurant = RestaurantPartner.objects.get(id=request.session['restaurant_id'])
        restaurant_name = request.session['restaurant_name']
        
        if request.method == 'POST':
            try:
                # Parse JSON data if it's an AJAX request
                if request.headers.get('Content-Type') == 'application/json':
                    data = json.loads(request.body)
                    action = data.get('action')
                    
                    if action == 'get_tables':
                        # Get tables filtered by restaurant name
                        tables = DiningTable.objects.filter(
                            restaurant=restaurant,
                            restaurant_name=restaurant_name
                        ).order_by('table_number')
                        
                        return JsonResponse({
                            'status': 'success',
                            'tables': [{
                                'id': table.id,
                                'table_number': table.table_number,
                                'category': table.category,
                                'seating_capacity': table.seating_capacity,
                                'price': float(table.price),
                                'rating': float(table.rating),
                                'status': table.status,
                                'image_url': table.image_url
                            } for table in tables]
                        })
                    
                    elif action == 'add':
                        # Verify restaurant name matches
                        if data.get('restaurant_name') != restaurant_name:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Invalid restaurant name'
                            })
                            
                        table = DiningTable.objects.create(
                            restaurant=restaurant,
                            restaurant_name=restaurant_name,
                            table_number=data.get('table_number'),
                            category=data.get('category'),
                            seating_capacity=data.get('seating_capacity'),
                            price=data.get('price'),
                            rating=data.get('rating'),
                            status=data.get('status'),
                            image_url=data.get('image_url')
                        )
                        
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Table added successfully',
                            'table': {
                                'id': table.id,
                                'table_number': table.table_number,
                                'category': table.category,
                                'seating_capacity': table.seating_capacity,
                                'price': float(table.price),
                                'rating': float(table.rating),
                                'status': table.status,
                                'image_url': table.image_url
                            }
                        })
                    
                    elif action == 'edit':
                        table_id = data.get('table_id')
                        if not table_id:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Table ID is required'
                            })
                        
                        table = DiningTable.objects.get(
                            id=table_id,
                            restaurant=restaurant,
                            restaurant_name=restaurant_name
                        )
                        
                        table.table_number = data.get('table_number', table.table_number)
                        table.category = data.get('category', table.category)
                        table.seating_capacity = data.get('seating_capacity', table.seating_capacity)
                        table.price = data.get('price', table.price)
                        table.rating = data.get('rating', table.rating)
                        table.status = data.get('status', table.status)
                        table.image_url = data.get('image_url', table.image_url)
                        table.save()
                        
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Table updated successfully',
                            'table': {
                                'id': table.id,
                                'table_number': table.table_number,
                                'category': table.category,
                                'seating_capacity': table.seating_capacity,
                                'price': float(table.price),
                                'rating': float(table.rating),
                                'status': table.status,
                                'image_url': table.image_url
                            }
                        })
                    
                    elif action == 'delete':
                        table_id = data.get('table_id')
                        if not table_id:
                            return JsonResponse({
                                'status': 'error',
                                'message': 'Table ID is required'
                            })
                        
                        table = DiningTable.objects.get(
                            id=table_id,
                            restaurant=restaurant,
                            restaurant_name=restaurant_name
                        )
                        table.delete()
                        
                        return JsonResponse({
                            'status': 'success',
                            'message': 'Table deleted successfully'
                        })
                
                return JsonResponse({
                    'status': 'error',
                    'message': 'Invalid action'
                })
                
            except DiningTable.DoesNotExist:
                return JsonResponse({
                    'status': 'error',
                    'message': 'Table not found'
                })
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        
        # Get all tables for this restaurant
        tables = DiningTable.objects.filter(
            restaurant=restaurant,
            restaurant_name=restaurant_name
        ).order_by('table_number')
        
        return render(request, 'partner/restaurant/dining_tables.html', {
            'restaurant': restaurant,
            'tables': tables
        })
        
    except RestaurantPartner.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Restaurant not found'
        }) if request.headers.get('Content-Type') == 'application/json' else redirect('joo:restaurant_login')

@csrf_exempt
def restaurant_booking_history(request):
    # Check if restaurant is logged in
    if 'restaurant_id' not in request.session or 'restaurant_name' not in request.session:
        return redirect('joo:restaurant_login')

    try:
        restaurant_name = request.session['restaurant_name']
        
        # Use the 'items' database connection where joo_order table exists
        with connections['items'].cursor() as cursor:
            # Get the orders using the restaurant name from session
            query = """
                SELECT order_id, customer_email, restaurant_id, 
                       restaurant_name, order_type, booking_date, status, items
                FROM public.joo_order 
                WHERE restaurant_name = %s
                AND order_type IN ('food', 'dining')
                ORDER BY booking_date DESC;
            """
            cursor.execute(query, [restaurant_name])
            
            columns = [col[0] for col in cursor.description]
            results = cursor.fetchall()
            
            joo_orders = []
            for row in results:
                order_dict = dict(zip(columns, row))
                joo_orders.append(order_dict)

    except Exception as e:
        print(f"Error: {str(e)}")
        joo_orders = []

    context = {
        'joo_orders': joo_orders,
        'restaurant_name': restaurant_name,
        'debug': True  # You can set this to False in production
    }
    
    return render(request, 'partner/restaurant/booking_history.html', context)

@csrf_exempt
def update_booking_status(request):
    if request.method == 'POST':
        try:
            data = json.loads(request.body)
            order_id = data.get('order_id')
            status = data.get('status')
            
            order = Order.objects.using('items').get(order_id=order_id)
            order.status = status
            order.save()
            
            return JsonResponse({
                'status': 'success',
                'message': 'Booking status updated successfully'
            })
            
        except Order.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Booking not found'
            })
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request method'
    })

@csrf_exempt
def venue_edit_profile(request):
    """Handle venue partner profile editing"""
    if 'venue_id' not in request.session:
        return redirect('joo:venue_login')
        
    venue = VenuePartner.objects.get(id=request.session['venue_id'])
    
    if request.method == 'POST':
        try:
            # Update venue fields from form data
            venue.venue_name = request.POST.get('venue_name', venue.venue_name)
            venue.owner_name = request.POST.get('owner_name', venue.owner_name)
            venue.email = request.POST.get('email', venue.email)
            venue.phone = request.POST.get('phone', venue.phone)
            venue.venue_type = request.POST.get('venue_type', venue.venue_type)
            venue.seating_capacity = request.POST.get('seating_capacity', venue.seating_capacity)
            venue.address = request.POST.get('address', venue.address)
            venue.venue_image = request.POST.get('venue_image', venue.venue_image)
            
            # Save the changes
            venue.save()
            
            # Update session data
            request.session['venue_name'] = venue.venue_name
            request.session['venue_image'] = venue.venue_image
            
            return JsonResponse({
                'status': 'success',
                'message': 'Profile updated successfully'
            })
            
        except Exception as e:
            return JsonResponse({
                'status': 'error',
                'message': str(e)
            })
    
    context = {
        'venue': venue
    }
    return render(request, 'partner/venue/edit_profile.html', context)

@csrf_exempt
def venue_packages(request):
    """Handle venue packages view"""
    if 'venue_id' not in request.session:
        return redirect('joo:venue_login')
    
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        
        # Get all packages for this venue
        packages = EventPackage.objects.filter(venue=venue).order_by('price')
        
        # Convert packages to list of dictionaries for JSON response
        packages_data = []
        for package in packages:
            packages_data.append({
                'id': package.id,
                'name': package.name,
                'description': package.description,
                'price': float(package.price),
                'max_guests': package.max_guests,
                'duration_hours': package.duration_hours,
                'is_active': package.is_active
            })
        
        if request.method == 'GET':
            return render(request, 'partner/venue/packages.html', {
                'venue': venue,
                'packages': packages
            })
        
        # For AJAX requests, return JSON data
        return JsonResponse({
            'status': 'success',
            'packages': packages_data
        })
        
    except VenuePartner.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('joo:venue_login')
    except Exception as e:
        print(f"Error loading packages: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error loading packages: {str(e)}'
        })

@csrf_exempt
def venue_events(request):
    """Handle venue events view"""
    if 'venue_id' not in request.session:
        return redirect('joo:venue_login')
    
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        
        # Get all events for this venue
        events = Event.objects.filter(venue=venue).order_by('-event_date')
        
        # Convert events to list of dictionaries for JSON response
        events_data = []
        for event in events:
            events_data.append({
                'id': event.id,
                'customer_name': event.customer_name,
                'customer_phone': event.customer_phone,
                'event_type': event.event_type,
                'event_date': event.event_date.strftime('%Y-%m-%d %H:%M'),
                'guest_count': event.guest_count,
                'package': event.package.name if event.package else None,
                'status': event.status,
                'rating': float(event.rating) if event.rating else None,
                'created_at': event.created_at.strftime('%Y-%m-%d %H:%M')
            })
        
        if request.method == 'GET':
            return render(request, 'partner/venue/events.html', {
                'venue': venue,
                'events': events,
                'status_choices': Event.STATUS_CHOICES
            })
        
        # For AJAX requests, return JSON data
        return JsonResponse({
            'status': 'success',
            'events': events_data
        })
        
    except VenuePartner.DoesNotExist:
        messages.error(request, "Venue not found")
        return redirect('joo:venue_login')
    except Exception as e:
        print(f"Error loading events: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error loading events: {str(e)}'
        })

@csrf_exempt
def update_event_status(request):
    """Handle updating event status"""
    if 'venue_id' not in request.session:
        return JsonResponse({
            'status': 'error',
            'message': 'Please login first'
        })
    
    if request.method != 'POST':
        return JsonResponse({
            'status': 'error',
            'message': 'Invalid request method'
        })
    
    try:
        data = json.loads(request.body)
        event_id = data.get('event_id')
        new_status = data.get('status')
        
        if not event_id or not new_status:
            return JsonResponse({
                'status': 'error',
                'message': 'Event ID and new status are required'
            })
        
        # Get the event and verify it belongs to this venue
        event = Event.objects.get(
            id=event_id,
            venue_id=request.session['venue_id']
        )
        
        # Validate the new status
        if new_status not in dict(Event.STATUS_CHOICES):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid status value'
            })
        
        # Update the status
        event.status = new_status
        event.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Event status updated successfully',
            'new_status': new_status,
            'event_id': event_id
        })
        
    except Event.DoesNotExist:
        return JsonResponse({
            'status': 'error',
            'message': 'Event not found or access denied'
        })
    except Exception as e:
        print(f"Error updating event status: {str(e)}")
        return JsonResponse({
            'status': 'error',
            'message': f'Error updating status: {str(e)}'
        })

@csrf_exempt
def venue_bookings(request):
    if 'venue_id' not in request.session:
        return redirect('joo:venue_login')
        
    try:
        venue = VenuePartner.objects.get(id=request.session['venue_id'])
        # Use Order model and filter for venue orders by restaurant_name and order_type
        bookings = Order.objects.using('items').filter(
            order_type='venue',  # Changed from 'table' to 'venue'
            restaurant_name=venue.venue_name  # Match by venue name instead of ID
        ).order_by('-booking_date')
        
        # Calculate statistics
        today = timezone.now().date()
        today_bookings = bookings.filter(booking_date__date=today)
        today_bookings_count = today_bookings.count()
        today_revenue = sum(b.total_amount for b in today_bookings) if today_bookings.exists() else 0
        
        pending_bookings_count = bookings.filter(status='pending').count()
        completed_bookings_count = bookings.filter(status='completed').count()
        total_bookings = bookings.count()
        completion_rate = (completed_bookings_count / total_bookings * 100) if total_bookings > 0 else 0
        
        # Calculate weekly revenue
        weekly_revenue = []
        for i in range(7):
            day = today - timedelta(days=i)
            day_bookings = bookings.filter(booking_date__date=day)
            amount = sum(b.total_amount for b in day_bookings) if day_bookings.exists() else 0
            max_amount = max((b.total_amount for b in bookings), default=1)
            weekly_revenue.append({
                'day': day.strftime('%a'),
                'amount': amount,
                'percentage': (amount / max_amount * 100) if max_amount > 0 else 0
            })
        weekly_revenue.reverse()
        
        context = {
            'venue': venue,
            'bookings': bookings,
            'today_bookings_count': today_bookings_count,
            'today_revenue': today_revenue,
            'pending_bookings_count': pending_bookings_count,
            'completed_bookings_count': completed_bookings_count,
            'completion_rate': round(completion_rate, 1),
            'weekly_revenue': weekly_revenue,
        }
        
        return render(request, 'partner/venue/bookings.html', context)
        
    except VenuePartner.DoesNotExist:
        return redirect('joo:venue_login')

@csrf_exempt
def delivery_edit_profile(request):
    """Handle delivery partner profile editing"""
    if 'delivery_id' not in request.session:
        return redirect('joo:delivery_login')
    
    try:
        delivery = DeliveryPartner.objects.get(id=request.session['delivery_id'])
        
        if request.method == 'POST':
            try:
                # Update basic info
                delivery.full_name = request.POST.get('full_name', delivery.full_name)
                delivery.phone = request.POST.get('phone', delivery.phone)
                delivery.vehicle_type = request.POST.get('vehicle_type', delivery.vehicle_type)
                delivery.vehicle_number = request.POST.get('vehicle_number', delivery.vehicle_number)
                delivery.license_number = request.POST.get('license_number', delivery.license_number)
                
                # Handle password update
                new_password = request.POST.get('new_password')
                if new_password:
                    delivery.password = hashlib.sha256(new_password.encode()).hexdigest()
                
                delivery.save()
                
                # Update session data
                request.session['delivery_name'] = delivery.full_name
                
                return JsonResponse({
                    'status': 'success',
                    'message': 'Profile updated successfully'
                })
                
            except Exception as e:
                return JsonResponse({
                    'status': 'error',
                    'message': str(e)
                })
        
        # For GET requests, render the template
        return render(request, 'partner/delivery/edit_profile.html', {
            'delivery': delivery
        })
        
    except DeliveryPartner.DoesNotExist:
        messages.error(request, "Delivery partner not found")
        return redirect('joo:delivery_login')

@csrf_exempt
def delivery_logout(request):
    """Handle delivery partner logout"""
    request.session.flush()
    return redirect('joo:delivery_login')

@csrf_exempt
def partner_login(request):
    """Handle main partner login page"""
    return render(request, 'login/partner.html')

@csrf_exempt
def send_reset_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        partner_type = data.get('partner_type')
        
        # Verify email exists for partner type
        partner_model = {
            'restaurant': RestaurantPartner,
            'venue': VenuePartner,
            'delivery': DeliveryPartner
        }.get(partner_type)
        
        try:
            partner = partner_model.objects.get(email=email)
            # Generate OTP
            otp = ''.join([str(random.randint(0, 9)) for _ in range(4)])
            
            # Save reset password request
            reset_request = ResetPassword.objects.create(
                email=email,
                partner_type=partner_type,
                otp=otp
            )
            
            # Send OTP email
            send_mail(
                'Password Reset OTP',
                f'Your OTP for password reset is: {otp}',
                'noreply@example.com',
                [email],
                fail_silently=False,
            )
            
            return JsonResponse({'status': 'success'})
            
        except partner_model.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Email not found'
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })

@csrf_exempt
def verify_reset_otp(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        otp = data.get('otp')
        
        try:
            reset_request = ResetPassword.objects.get(
                email=email,
                otp=otp,
                is_verified=False,
                expires_at__gt=timezone.now()
            )
            
            reset_request.is_verified = True
            reset_request.save()
            
            return JsonResponse({'status': 'success'})
            
        except ResetPassword.DoesNotExist:
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid or expired OTP'
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })

@csrf_exempt
def update_password(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        email = data.get('email')
        partner_type = data.get('partner_type')
        new_password = data.get('new_password')
        
        try:
            # Verify reset request
            reset_request = ResetPassword.objects.get(
                email=email,
                partner_type=partner_type,
                is_verified=True,
                expires_at__gt=timezone.now()
            )
            
            # Update partner password using hashlib.sha256
            hashed_password = hashlib.sha256(new_password.encode()).hexdigest()
            
            # Update partner password
            partner_model = {
                'restaurant': RestaurantPartner,
                'venue': VenuePartner,
                'delivery': DeliveryPartner
            }.get(partner_type)
            
            partner = partner_model.objects.get(email=email)
            partner.password = hashed_password
            partner.save()
            
            # Delete reset request
            reset_request.delete()
            
            # Return success with redirect URL
            redirect_urls = {
                'restaurant': 'joo:restaurant_login',
                'venue': 'joo:venue_login',
                'delivery': 'joo:delivery_login'
            }
            
            return JsonResponse({
                'status': 'success',
                'redirect_url': reverse(redirect_urls[partner_type])
            })
            
        except (ResetPassword.DoesNotExist, partner_model.DoesNotExist):
            return JsonResponse({
                'status': 'error',
                'message': 'Invalid reset request'
            })
            
    return JsonResponse({
        'status': 'error',
        'message': 'Invalid request'
    })
        