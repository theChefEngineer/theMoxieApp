# utils/constants.py
from django.utils.translation import gettext_lazy as _

# Status Choices
APPOINTMENT_STATUS_CHOICES = [
    ('scheduled', _('Scheduled')),
    ('confirmed', _('Confirmed')),
    ('in_progress', _('In Progress')),
    ('completed', _('Completed')),
    ('canceled', _('Canceled')),
    ('no_show', _('No Show')),
]

# Service Categories and Types
SERVICE_CATEGORIES = {
    'injectables': {
        'types': [
            'neuromodulators',
            'HA dermal filler',
            'Calcium Hydroxyapatite'
        ],
        'description': _('Injectable treatments for cosmetic enhancement')
    },
    'peels': {
        'types': [
            'chemical peel',
            'enzyme peel'
        ],
        'description': _('Skin renewal and rejuvenation treatments')
    },
    'threads': {
        'types': [
            'PDO threads',
            'PLLA threads'
        ],
        'description': _('Thread lifting and skin tightening treatments')
    }
}

# Time Constants
BUSINESS_HOURS = {
    'start': 9,  # 9 AM
    'end': 17,   # 5 PM
}

APPOINTMENT_DURATION_LIMITS = {
    'min': 15,    # 15 minutes
    'max': 480,   # 8 hours
}

# Cache Keys
CACHE_KEYS = {
    'medspa_services': 'medspa_{}_services',
    'appointment_details': 'appointment_{}',
    'service_categories': 'service_categories',
}

# Error Messages
ERROR_MESSAGES = {
    'invalid_phone': _('Invalid phone number format'),
    'past_date': _('Date cannot be in the past'),
    'outside_hours': _('Time must be within business hours'),
    'duration_exceeded': _('Duration exceeds maximum allowed time'),
    'invalid_status': _('Invalid status transition'),
    'service_conflict': _('Service scheduling conflict detected'),
}

# Pagination
PAGINATION = {
    'default_page_size': 10,
    'max_page_size': 100,
}

# Rate Limiting
RATE_LIMITS = {
    'anon': '100/hour',
    'user': '1000/hour',
    'staff': '5000/hour',
}
