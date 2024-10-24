# utils/helpers.py
from datetime import datetime, timedelta
from django.utils import timezone
from django.db.models import Sum, Count, Avg
from decimal import Decimal
import logging

logger = logging.getLogger(__name__)

def calculate_appointment_metrics(appointment):
    """Calculate total duration and price for an appointment."""
    services = appointment.services.all()
    
    total_duration = services.aggregate(
        total_duration=Sum('duration')
    )['total_duration'] or 0
    
    total_price = services.aggregate(
        total_price=Sum('price')
    )['total_price'] or Decimal('0')
    
    return {
        'total_duration': total_duration,
        'total_price': total_price
    }

def get_available_slots(medspa, date, duration=60):
    """Get available appointment slots for a given date."""
    from .constants import BUSINESS_HOURS
    
    # Convert date to datetime objects for start and end of business day
    start_time = datetime.combine(date, datetime.min.time().replace(
        hour=BUSINESS_HOURS['start']
    ))
    end_time = datetime.combine(date, datetime.min.time().replace(
        hour=BUSINESS_HOURS['end']
    ))
    
    # Get all appointments for the day
    existing_appointments = medspa.appointments.filter(
        start_time__date=date
    ).values_list('start_time', 'services__duration')
    
    # Create list of all possible slots
    all_slots = []
    current_slot = start_time
    while current_slot + timedelta(minutes=duration) <= end_time:
        slot_end = current_slot + timedelta(minutes=duration)
        
        # Check if slot conflicts with existing appointments
        is_available = True
        for appt_start, appt_duration in existing_appointments:
            appt_end = appt_start + timedelta(minutes=appt_duration or 0)
            if (current_slot < appt_end and slot_end > appt_start):
                is_available = False
                break
        
        if is_available:
            all_slots.append(current_slot)
        
        current_slot += timedelta(minutes=30)  # 30-minute intervals
    
    return all_slots

def generate_medspa_report(medspa, start_date=None, end_date=None):
    """Generate statistical report for a medspa."""
    if not start_date:
        start_date = timezone.now() - timedelta(days=30)
    if not end_date:
        end_date = timezone.now()

    appointments = medspa.appointments.filter(
        start_time__range=(start_date, end_date)
    )
    
    completed_appointments = appointments.filter(status='completed')
    
    report = {
        'period': {
            'start': start_date,
            'end': end_date,
        },
        'appointments': {
            'total': appointments.count(),
            'completed': completed_appointments.count(),
            'canceled': appointments.filter(status='canceled').count(),
            'no_show': appointments.filter(status='no_show').count(),
        },
        'services': {
            'total': medspa.services.count(),
            'most_popular': medspa.services.annotate(
                usage_count=Count('appointmentservice')
            ).order_by('-usage_count').first(),
        },
        'revenue': {
            'total': completed_appointments.aggregate(
                total=Sum('services__price')
            )['total'] or 0,
            'average_per_appointment': completed_appointments.annotate(
                total=Sum('services__price')
            ).aggregate(avg=Avg('total'))['avg'] or 0,
        }
    }
    
    return report

def format_phone_number(phone):
    """Format phone number to consistent format."""
    import re
    # Remove all non-digit characters
    cleaned = re.sub(r'\D', '', phone)
    
    # Format as (XXX) XXX-XXXX
    if len(cleaned) == 10:
        return f"({cleaned[:3]}) {cleaned[3:6]}-{cleaned[6:]}"
    return phone

def calculate_service_utilization(service, period_days=30):
    """Calculate utilization statistics for a service."""
    end_date = timezone.now()
    start_date = end_date - timedelta(days=period_days)
    
    appointments = service.appointmentservice_set.filter(
        appointment__start_time__range=(start_date, end_date),
        appointment__status='completed'
    )
    
    total_appointments = appointments.count()
    total_revenue = appointments.aggregate(
        total=Sum('service__price')
    )['total'] or 0
    
    return {
        'period_days': period_days,
        'total_appointments': total_appointments,
        'average_appointments_per_day': total_appointments / period_days,
        'total_revenue': total_revenue,
        'average_revenue_per_day': total_revenue / period_days
    }
