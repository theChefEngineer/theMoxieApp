from rest_framework import serializers
from .models import (
    Medspa,
    Service,
    Appointment,
    AppointmentService,
    ServiceCategory,
    ServiceType
)
from django.db.models import Sum
from decimal import Decimal


class ServiceCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ServiceCategory
        fields = ['id', 'name', 'description']


class ServiceTypeSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)

    class Meta:
        model = ServiceType
        fields = ['id', 'category', 'category_name', 'name', 'description']


class MedspaSerializer(serializers.ModelSerializer):
    total_services = serializers.IntegerField(read_only=True)
    total_appointments = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Medspa
        fields = [
            'id', 'name', 'address', 'phone_number', 'email_address',
            'total_services', 'total_appointments', 'created_at', 'updated_at'
        ]

    def to_representation(self, instance):
        data = super().to_representation(instance)
        data['total_services'] = instance.services.filter(active=True).count()
        data['total_appointments'] = instance.appointments.count()
        return data

    def validate_phone_number(self, value):
        if value:
            # Remove any non-numeric characters
            cleaned_number = ''.join(filter(str.isdigit, value))
            if len(cleaned_number) < 10:
                raise serializers.ValidationError("Phone number must have at least 10 digits")
            return cleaned_number
        return value


class ServiceSerializer(serializers.ModelSerializer):
    medspa_name = serializers.CharField(source='medspa.name', read_only=True)
    category_name = serializers.CharField(source='category.name', read_only=True)
    service_type_name = serializers.CharField(source='service_type.name', read_only=True)
    appointment_count = serializers.IntegerField(read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Service
        fields = [
            'id', 'name', 'description', 'price', 'duration',
            'medspa', 'medspa_name', 'category', 'category_name',
            'service_type', 'service_type_name', 'product', 'supplier',
            'active', 'appointment_count', 'created_at', 'updated_at'
        ]

    def validate_price(self, value):
        if value <= Decimal('0'):
            raise serializers.ValidationError("Price must be greater than zero")
        return value

    def validate_duration(self, value):
        if value <= 0:
            raise serializers.ValidationError("Duration must be greater than zero")
        return value

    def validate(self, data):
        # Validate that service_type belongs to the selected category
        category = data.get('category')
        service_type = data.get('service_type')

        if category and service_type and service_type.category != category:
            raise serializers.ValidationError({
                'service_type': 'Selected service type does not belong to the selected category'
            })

        return data


class AppointmentServiceSerializer(serializers.ModelSerializer):
    service_name = serializers.CharField(source='service.name', read_only=True)
    price = serializers.DecimalField(source='service.price', max_digits=10, decimal_places=2, read_only=True)
    duration = serializers.IntegerField(source='service.duration', read_only=True)
    category_name = serializers.CharField(source='service.category.name', read_only=True)
    service_type_name = serializers.CharField(source='service.service_type.name', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = AppointmentService
        fields = [
            'service', 'service_name', 'price', 'duration',
            'category_name', 'service_type_name', 'created_at'
        ]


class AppointmentSerializer(serializers.ModelSerializer):
    services = AppointmentServiceSerializer(source='appointmentservice_set', many=True)
    total_duration = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(
        max_digits=10, decimal_places=2, read_only=True
    )
    medspa_name = serializers.CharField(source='medspa.name', read_only=True)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)

    class Meta:
        model = Appointment
        fields = [
            'id', 'start_time', 'status', 'medspa', 'medspa_name',
            'services', 'total_duration', 'total_price',
            'created_at', 'updated_at'
        ]

    def validate_start_time(self, value):
        """Validate that appointment start time is not in the past"""
        from django.utils import timezone
        if value < timezone.now():
            raise serializers.ValidationError(
                "Appointment cannot be scheduled in the past"
            )
        return value

    def validate_services(self, services):
        """Validate services for the appointment"""
        if not services:
            raise serializers.ValidationError(
                "At least one service is required"
            )

        # Check if all services belong to the same medspa
        medspa_id = self.initial_data.get('medspa')
        if medspa_id:
            for service_data in services:
                service_id = service_data.get('service')
                try:
                    service = Service.objects.get(id=service_id)
                    if not service.active:
                        raise serializers.ValidationError(
                            f"Service {service.name} is not currently active"
                        )
                    if service.medspa_id != int(medspa_id):
                        raise serializers.ValidationError(
                            f"Service {service.name} does not belong to the selected medspa"
                        )
                except Service.DoesNotExist:
                    raise serializers.ValidationError(
                        f"Service with id {service_id} does not exist"
                    )

        return services

    def create(self, validated_data):
        """Create appointment with services"""
        services_data = validated_data.pop('appointmentservice_set', [])
        appointment = Appointment.objects.create(**validated_data)

        # Calculate total price and duration
        total_price = Decimal('0')
        total_duration = 0

        # Add services and calculate totals
        for service_data in services_data:
            service = service_data['service']
            AppointmentService.objects.create(
                appointment=appointment,
                service=service
            )
            total_price += service.price
            total_duration += service.duration

        appointment.total_price = total_price
        appointment.save()

        return appointment

    def update(self, instance, validated_data):
        """Update appointment and its services"""
        services_data = validated_data.pop('appointmentservice_set', None)

        # Update appointment fields
        for attr, value in validated_data.items():
            setattr(instance, attr, value)

        # Update services if provided
        if services_data is not None:
            # Remove existing services
            instance.appointmentservice_set.all().delete()

            # Add new services
            total_price = Decimal('0')
            total_duration = 0

            for service_data in services_data:
                service = service_data['service']
                AppointmentService.objects.create(
                    appointment=instance,
                    service=service
                )
                total_price += service.price
                total_duration += service.duration

            instance.total_price = total_price

        instance.save()
        return instance

    def to_representation(self, instance):
        """Add calculated fields to the representation"""
        data = super().to_representation(instance)

        # Calculate totals from related services
        services = data.get('services', [])
        data['total_duration'] = sum(
            service['duration'] for service in services
        )
        data['total_price'] = str(sum(
            Decimal(str(service['price'])) for service in services
        ))

        return data
