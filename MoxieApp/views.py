from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from django.utils import timezone
from django.db.models import Sum, Count, Q, Avg, F
from datetime import datetime, time
from decimal import Decimal

from .models import (
    Medspa,
    Service,
    Appointment,
    ServiceCategory,
    ServiceType
)
from .serializers import (
    MedspaSerializer,
    ServiceSerializer,
    AppointmentSerializer,
    ServiceCategorySerializer,
    ServiceTypeSerializer
)
from .utils.custom_exceptions import ServiceValidationError, AppointmentValidationError
from .utils.decorators import (
    log_action,
    measure_execution_time,
    cache_response,
    atomic_transaction,
    validate_request_data,
    require_permissions,
    rate_limit,
    handle_exceptions
)
import logging

logger = logging.getLogger(__name__)


class ServiceCategoryViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service categories.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ServiceCategory.objects.all()
    serializer_class = ServiceCategorySerializer

    @handle_exceptions
    @cache_response(timeout=3600)  # Cache for 1 hour
    def list(self, request, *args, **kwargs):
        return super().list(request, *args, **kwargs)


class ServiceTypeViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing service types.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = ServiceType.objects.all()
    serializer_class = ServiceTypeSerializer

    @handle_exceptions
    @measure_execution_time
    def get_queryset(self):
        queryset = super().get_queryset()
        category_id = self.request.query_params.get('category_id')
        if category_id:
            queryset = queryset.filter(category_id=category_id)
        return queryset


class MedspaViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing medspa operations.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    queryset = Medspa.objects.all()
    serializer_class = MedspaSerializer

    @handle_exceptions
    @atomic_transaction
    @validate_request_data('name', 'email_address')
    @require_permissions('can_create_medspa')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @handle_exceptions
    @atomic_transaction
    @require_permissions('can_update_medspa')
    def update(self, request, *args, **kwargs):
        return super().update(request, *args, **kwargs)

    @handle_exceptions
    @cache_response(timeout=300)
    @measure_execution_time
    @log_action("medspa_statistics")
    @action(detail=True)
    def statistics(self, request, pk=None):
        """Get statistics for a specific medspa."""
        medspa = self.get_object()
        today = timezone.now()

        stats = {
            'total_services': medspa.services.filter(active=True).count(),
            'total_appointments': medspa.appointments.count(),
            'appointments_today': medspa.appointments.filter(
                start_time__date=today.date()
            ).count(),
            'revenue': medspa.appointments.filter(
                status='completed'
            ).aggregate(
                total=Sum(F('services__price'))
            )['total'] or Decimal('0.00'),
            'active_categories': ServiceCategory.objects.filter(
                services__medspa=medspa,
                services__active=True
            ).distinct().count(),
        }

        return Response(stats)

    @handle_exceptions
    @validate_request_data('date')
    @rate_limit(calls=100, period=3600)
    @log_action("medspa_availability")
    @action(detail=True)
    def availability(self, request, pk=None):
        """Get availability slots for a specific medspa."""
        medspa = self.get_object()
        date = request.query_params.get('date')

        try:
            target_date = datetime.strptime(date, '%Y-%m-%d').date()

            # Get all booked appointments for the date
            booked_appointments = medspa.appointments.filter(
                start_time__date=target_date,
                status='scheduled'
            ).values_list('start_time', 'services__duration')

            # Create time slots
            all_slots = []
            for hour in range(9, 17):  # 9 AM to 5 PM
                slot_time = datetime.combine(target_date, time(hour=hour))
                # Check if slot is available
                is_available = not any(
                    booked_start <= slot_time < booked_start + timezone.timedelta(minutes=duration)
                    for booked_start, duration in booked_appointments
                )
                if is_available:
                    all_slots.append(slot_time)

            return Response({
                'date': date,
                'available_slots': all_slots
            })

        except ValueError:
            return Response(
                {'error': 'Invalid date format. Use YYYY-MM-DD'},
                status=status.HTTP_400_BAD_REQUEST
            )


class ServiceViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing services.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = ServiceSerializer

    @handle_exceptions
    @measure_execution_time
    def get_queryset(self):
        queryset = Service.objects.select_related(
            'medspa', 'category', 'service_type'
        ).prefetch_related('appointments')

        # Apply filters
        filters = {}

        medspa_id = self.request.query_params.get('medspa_id')
        if medspa_id:
            filters['medspa_id'] = medspa_id

        category_id = self.request.query_params.get('category_id')
        if category_id:
            filters['category_id'] = category_id

        service_type_id = self.request.query_params.get('service_type_id')
        if service_type_id:
            filters['service_type_id'] = service_type_id

        active = self.request.query_params.get('active')
        if active is not None:
            filters['active'] = active.lower() == 'true'

        min_price = self.request.query_params.get('min_price')
        max_price = self.request.query_params.get('max_price')
        if min_price:
            filters['price__gte'] = Decimal(min_price)
        if max_price:
            filters['price__lte'] = Decimal(max_price)

        queryset = queryset.filter(**filters)

        return queryset.annotate(
            appointment_count=Count('appointments')
        )

    @handle_exceptions
    @atomic_transaction
    @validate_request_data('name', 'price', 'duration', 'medspa', 'category', 'service_type')
    @require_permissions('can_create_service')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @handle_exceptions
    @cache_response(timeout=300)
    @measure_execution_time
    @log_action("service_usage_statistics")
    @action(detail=True)
    def usage_statistics(self, request, pk=None):
        """Get usage statistics for a specific service."""
        service = self.get_object()

        completed_appointments = service.appointments.filter(
            status='completed'
        )

        stats = {
            'total_appointments': service.appointments.count(),
            'completed_appointments': completed_appointments.count(),
            'revenue': completed_appointments.aggregate(
                total=Sum('services__price')
            )['total'] or Decimal('0.00'),
            'average_duration': service.duration,
            'category': service.category.name,
            'service_type': service.service_type.name,
        }

        return Response(stats)


class AppointmentViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing appointments.
    """
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]
    serializer_class = AppointmentSerializer

    @handle_exceptions
    @measure_execution_time
    def get_queryset(self):
        queryset = Appointment.objects.select_related(
            'medspa'
        ).prefetch_related(
            'services',
            'services__category',
            'services__service_type'
        )

        # Apply filters
        filters = {}

        status_filter = self.request.query_params.get('status')
        if status_filter:
            filters['status'] = status_filter

        date_filter = self.request.query_params.get('date')
        if date_filter:
            try:
                filter_date = datetime.strptime(date_filter, '%Y-%m-%d').date()
                filters['start_time__date'] = filter_date
            except ValueError:
                pass

        medspa_id = self.request.query_params.get('medspa_id')
        if medspa_id:
            filters['medspa_id'] = medspa_id

        return queryset.filter(**filters)

    @handle_exceptions
    @atomic_transaction
    @validate_request_data('start_time', 'medspa', 'services')
    @require_permissions('can_create_appointment')
    def create(self, request, *args, **kwargs):
        return super().create(request, *args, **kwargs)

    @handle_exceptions
    @atomic_transaction
    @validate_request_data('status')
    @log_action("appointment_status_update")
    @action(detail=True, methods=['patch'])
    def update_status(self, request, pk=None):
        """Update the status of an appointment."""
        try:
            appointment = self.get_object()
            new_status = request.data.get('status')

            if new_status not in dict(Appointment.STATUS_CHOICES):
                raise AppointmentValidationError("Invalid status value")

            appointment.status = new_status
            appointment.save()

            logger.info(f"Updated appointment {appointment.id} status to {new_status}")
            return Response(self.get_serializer(appointment).data)

        except Exception as e:
            logger.error(f"Error updating appointment status: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )

    @handle_exceptions
    @cache_response(timeout=300)
    @measure_execution_time
    @log_action("appointment_calendar")
    @action(detail=False)
    def calendar(self, request):
        """Get calendar view of appointments."""
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        medspa_id = request.query_params.get('medspa_id')

        queryset = self.get_queryset()

        if medspa_id:
            queryset = queryset.filter(medspa_id=medspa_id)

        if start_date:
            queryset = queryset.filter(start_time__date__gte=start_date)
        if end_date:
            queryset = queryset.filter(start_time__date__lte=end_date)

        calendar_data = queryset.values(
            'id', 'start_time', 'status', 'medspa__name'
        ).annotate(
            service_count=Count('services'),
            total_duration=Sum('services__duration'),
            total_price=Sum('services__price')
        ).order_by('start_time')

        return Response(calendar_data)

    @handle_exceptions
    @cache_response(timeout=300)
    @measure_execution_time
    @log_action("appointment_analytics")
    @action(detail=False)
    def analytics(self, request):
        """Get appointment analytics."""
        days = int(request.query_params.get('days', 30))
        end_date = timezone.now()
        start_date = end_date - timezone.timedelta(days=days)

        # Get base queryset for the time period
        queryset = self.get_queryset().filter(
            start_time__date__range=[start_date.date(), end_date.date()]
        )

        # Calculate analytics
        total_appointments = queryset.count()
        completed_appointments = queryset.filter(status='completed')
        canceled_appointments = queryset.filter(status='canceled')

        analytics = {
            'period': {
                'start_date': start_date.date(),
                'end_date': end_date.date(),
                'days': days
            },
            'appointments': {
                'total': total_appointments,
                'completed': completed_appointments.count(),
                'canceled': canceled_appointments.count(),
                'scheduled': queryset.filter(status='scheduled').count()
            },
            'revenue': completed_appointments.aggregate(
                total=Sum('services__price')
            )['total'] or Decimal('0.00'),
            'services': {
                'average_per_appointment': queryset.annotate(
                    service_count=Count('services')
                ).aggregate(avg=Avg('service_count'))['avg'] or 0,
                'most_popular': queryset.values(
                    'services__name'
                ).annotate(
                    count=Count('services__name')
                ).order_by('-count')[:5]
            },
            'categories': {
                'distribution': completed_appointments.values(
                    'services__category__name'
                ).annotate(
                    count=Count('services__category'),
                    revenue=Sum('services__price')
                ).order_by('-count')
            }
        }

        return Response(analytics)
