# utils/validators.py
import re
from datetime import datetime
from django.core.exceptions import ValidationError
from django.utils import timezone

def validate_phone_number(phone_number):
    """
    Validate phone number format.
    Accepts formats: (XXX) XXX-XXXX, XXX-XXX-XXXX, XXXXXXXXXX
    """
    pattern = r'^\(?([0-9]{3})\)?[-. ]?([0-9]{3})[-. ]?([0-9]{4})$'
    if not re.match(pattern, phone_number):
        raise ValidationError("Invalid phone number format")
    return phone_number

def validate_future_date(date):
    """Validate that a date is in the future."""
    if date < timezone.now():
        raise ValidationError("Date must be in the future")
    return date

def validate_business_hours(datetime_obj):
    """Validate that datetime falls within business hours (9 AM - 5 PM)."""
    if datetime_obj.hour < 9 or datetime_obj.hour >= 17:
        raise ValidationError("Appointments must be scheduled between 9 AM and 5 PM")
    return datetime_obj

def validate_service_category(category, service_type):
    """Validate service category and type combinations."""
    valid_combinations = {
        'injectables': ['neuromodulators', 'HA dermal filler', 'Calcium Hydroxyapatite'],
        'peels': ['chemical peel', 'enzyme peel'],
        'threads': ['PDO threads', 'PLLA threads']
    }
    
    if category not in valid_combinations:
        raise ValidationError(f"Invalid category: {category}")
    
    if service_type not in valid_combinations[category]:
        raise ValidationError(f"Invalid service type '{service_type}' for category '{category}'")
    
    return True

def validate_price(price):
    """Validate price is positive and has max 2 decimal places."""
    from decimal import Decimal
    if not isinstance(price, (int, float, Decimal)):
        raise ValidationError("Price must be a number")
    
    price = Decimal(str(price))
    if price <= 0:
        raise ValidationError("Price must be greater than zero")
    
    if abs(price.as_tuple().exponent) > 2:
        raise ValidationError("Price cannot have more than 2 decimal places")
    
    return price

def validate_duration(duration):
    """Validate service duration."""
    if not isinstance(duration, int):
        raise ValidationError("Duration must be an integer")
    
    if duration <= 0:
        raise ValidationError("Duration must be greater than zero")
    
    if duration > 480:  # 8 hours
        raise ValidationError("Duration cannot exceed 8 hours")
    
    return duration
