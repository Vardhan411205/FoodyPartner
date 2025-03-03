from django.core.serializers.json import DjangoJSONEncoder
import json
from rest_framework import serializers
from joo.models import VenuePartner

class OrderItemsEncoder(DjangoJSONEncoder):
    def default(self, obj):
        if isinstance(obj, (list, dict)):
            return json.dumps(obj)
        return super().default(obj)

def parse_order_items(items_json):
    """Parse order items from JSON string"""
    try:
        return json.loads(items_json)
    except:
        return []

class VenuePartnerSerializer(serializers.ModelSerializer):
    class Meta:
        model = VenuePartner
        fields = ['id', 'venue_name', 'owner_name', 'email', 'phone', 
                 'venue_type', 'seating_capacity', 'price', 'address', 
                 'venue_image', 'is_active'] 