from django.core.exceptions import ValidationError
from .models import FoodItem, RestaurantPartner
from django.core.files.storage import FileSystemStorage
import os
from decimal import Decimal

class FoodItemManager:
    @staticmethod
    def add_food_item(restaurant, name, price, category, image_url, rating=0.0):
        try:
            # Convert price and rating to Decimal
            price = Decimal(str(price))
            rating = Decimal(str(rating))
            
            # Validate rating range
            if rating < 0 or rating > 5:
                raise ValidationError('Rating must be between 0 and 5')
            
            food_item = FoodItem.objects.create(
                restaurant=restaurant,
                name=name,
                price=price,
                category=category,
                image_url=image_url,
                rating=rating
            )
            
            return {
                'status': 'success',
                'message': 'Food item added successfully',
                'item_id': food_item.id
            }
        except Exception as e:
            raise ValidationError(f'Error adding food item: {str(e)}')

    @staticmethod
    def update_food_item(item_id, restaurant, updates):
        try:
            food_item = FoodItem.objects.get(id=item_id, restaurant=restaurant)
            
            # Update fields
            if 'name' in updates:
                food_item.name = updates['name']
            if 'price' in updates:
                food_item.price = Decimal(str(updates['price']))
            if 'category' in updates:
                food_item.category = updates['category']
            if 'image_url' in updates:
                food_item.image_url = updates['image_url']
            if 'rating' in updates:
                rating = Decimal(str(updates['rating']))
                if rating < 0 or rating > 5:
                    raise ValidationError('Rating must be between 0 and 5')
                food_item.rating = rating
            
            food_item.save()
            return {
                'status': 'success',
                'message': 'Food item updated successfully'
            }
        except FoodItem.DoesNotExist:
            raise ValidationError('Food item not found')
        except Exception as e:
            raise ValidationError(f'Error updating food item: {str(e)}')

    @staticmethod
    def delete_food_item(item_id, restaurant):
        try:
            food_item = FoodItem.objects.get(id=item_id, restaurant=restaurant)
            food_item.delete()
            return {
                'status': 'success',
                'message': 'Food item deleted successfully'
            }
        except FoodItem.DoesNotExist:
            raise ValidationError('Food item not found')
        except Exception as e:
            raise ValidationError(f'Error deleting food item: {str(e)}')

    @staticmethod
    def toggle_availability(item_id, restaurant_email):
        try:
            # Get food item and verify ownership
            food_item = FoodItem.objects.get(
                id=item_id, 
                restaurant_email__email=restaurant_email
            )
            
            # Toggle availability
            food_item.is_available = not food_item.is_available
            food_item.save()
            
            return {
                'status': 'success',
                'message': f'Food item is now {"available" if food_item.is_available else "unavailable"}'
            }
            
        except FoodItem.DoesNotExist:
            raise ValidationError('Food item not found or unauthorized')
        except Exception as e:
            raise ValidationError(f'Error toggling availability: {str(e)}')

    @staticmethod
    def get_restaurant_food_items(restaurant_email, category=None):
        try:
            # Base query
            query = FoodItem.objects.filter(restaurant_email__email=restaurant_email)
            
            # Apply category filter if specified
            if category:
                query = query.filter(category=category)
            
            # Order by name
            food_items = query.order_by('name')
            
            return food_items
            
        except Exception as e:
            raise ValidationError(f'Error fetching food items: {str(e)}') 