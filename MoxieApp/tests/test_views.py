from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from ..models import (
    Medspa,
    Service,
    Appointment,
    ServiceCategory,
    ServiceType
)
from datetime import datetime, timedelta
from decimal import Decimal
import json


class TestMedspaViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create base test data
        self.medspa_data = {
            "name": "New Medspa",
            "email_address": "new@medspa.com",
            "phone_number": "123-456-7890",
            "address": "123 Test St"
        }

    def test_create_medspa(self):
        """Test medspa creation endpoint"""
        response = self.client.post(
            reverse('medspa-list'),
            self.medspa_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Medspa.objects.count(), 1)
        self.assertEqual(response.data['name'], "New Medspa")

    def test_list_medspas(self):
        """Test retrieving list of medspas"""
        # Create multiple medspas
        Medspa.objects.create(**self.medspa_data)
        Medspa.objects.create(
            name="Second Medspa",
            email_address="second@medspa.com",
            phone_number="987-654-3210"
        )

        response = self.client.get(reverse('medspa-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 2)

    def test_retrieve_medspa(self):
        """Test retrieving single medspa"""
        medspa = Medspa.objects.create(**self.medspa_data)
        response = self.client.get(
            reverse('medspa-detail', kwargs={'pk': medspa.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['email_address'], "new@medspa.com")

    def test_medspa_statistics(self):
        """Test medspa statistics endpoint"""
        medspa = Medspa.objects.create(**self.medspa_data)
        response = self.client.get(
            reverse('medspa-statistics', kwargs={'pk': medspa.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_services', response.data)
        self.assertIn('total_appointments', response.data)

    def test_medspa_availability(self):
        """Test medspa availability endpoint"""
        medspa = Medspa.objects.create(**self.medspa_data)
        tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')

        response = self.client.get(
            reverse('medspa-availability', kwargs={'pk': medspa.id}),
            {'date': tomorrow}
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('available_slots', response.data)


class TestServiceViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create required related objects
        self.medspa = Medspa.objects.create(
            name="Test Medspa",
            email_address="test@medspa.com"
        )
        self.category = ServiceCategory.objects.create(
            name="Injectables",
            description="Injectable treatments"
        )
        self.service_type = ServiceType.objects.create(
            category=self.category,
            name="Neuromodulators",
            description="Botox and similar"
        )
        self.service_data = {
            "name": "New Service",
            "price": "199.99",
            "duration": 60,
            "medspa": self.medspa.id,
            "category": self.category.id,
            "service_type": self.service_type.id,
            "product": "botox",
            "supplier": "Allergan"
        }

    def test_create_service(self):
        """Test service creation"""
        response = self.client.post(
            reverse('service-list'),
            self.service_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Service.objects.count(), 1)
        self.assertEqual(response.data['name'], "New Service")

    def test_list_services(self):
        """Test retrieving list of services"""
        Service.objects.create(**{
            **self.service_data,
            "medspa": self.medspa,
            "category": self.category,
            "service_type": self.service_type
        })

        response = self.client.get(reverse('service-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_services(self):
        """Test service filtering"""
        Service.objects.create(**{
            **self.service_data,
            "medspa": self.medspa,
            "category": self.category,
            "service_type": self.service_type
        })

        # Test medspa filter
        response = self.client.get(
            f"{reverse('service-list')}?medspa_id={self.medspa.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test category filter
        response = self.client.get(
            f"{reverse('service-list')}?category_id={self.category.id}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_service_usage_statistics(self):
        """Test service usage statistics endpoint"""
        service = Service.objects.create(**{
            **self.service_data,
            "medspa": self.medspa,
            "category": self.category,
            "service_type": self.service_type
        })

        response = self.client.get(
            reverse('service-usage-statistics', kwargs={'pk': service.id})
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_appointments', response.data)
        self.assertIn('revenue', response.data)


class TestAppointmentViews(APITestCase):
    def setUp(self):
        self.client = APIClient()
        # Create required related objects
        self.medspa = Medspa.objects.create(
            name="Test Medspa",
            email_address="test@medspa.com"
        )
        self.category = ServiceCategory.objects.create(name="Injectables")
        self.service_type = ServiceType.objects.create(
            category=self.category,
            name="Neuromodulators"
        )
        self.service = Service.objects.create(
            name="Test Service",
            price=Decimal("199.99"),
            duration=60,
            medspa=self.medspa,
            category=self.category,
            service_type=self.service_type
        )
        self.appointment_data = {
            "start_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "medspa": self.medspa.id,
            "services": [self.service.id]
        }

    def test_create_appointment(self):
        """Test appointment creation"""
        response = self.client.post(
            reverse('appointment-list'),
            self.appointment_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(Appointment.objects.count(), 1)
        self.assertEqual(
            Decimal(response.data['total_price']),
            Decimal("199.99")
        )

    def test_list_appointments(self):
        """Test retrieving list of appointments"""
        appointment = Appointment.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            medspa=self.medspa
        )
        appointment.services.add(self.service)

        response = self.client.get(reverse('appointment-list'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_filter_appointments(self):
        """Test appointment filtering"""
        appointment = Appointment.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            medspa=self.medspa,
            status='scheduled'
        )
        appointment.services.add(self.service)

        # Test status filter
        response = self.client.get(
            f"{reverse('appointment-list')}?status=scheduled"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

        # Test date filter
        tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        response = self.client.get(
            f"{reverse('appointment-list')}?date={tomorrow}"
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_update_appointment_status(self):
        """Test appointment status update"""
        appointment = Appointment.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            medspa=self.medspa
        )
        appointment.services.add(self.service)

        response = self.client.patch(
            reverse('appointment-update-status', kwargs={'pk': appointment.id}),
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['status'], 'completed')

    def test_appointment_calendar(self):
        """Test appointment calendar endpoint"""
        appointment = Appointment.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            medspa=self.medspa
        )
        appointment.services.add(self.service)

        response = self.client.get(reverse('appointment-calendar'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)

    def test_appointment_analytics(self):
        """Test appointment analytics endpoint"""
        appointment = Appointment.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            medspa=self.medspa,
            status='completed'
        )
        appointment.services.add(self.service)

        response = self.client.get(reverse('appointment-analytics'))
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('total_appointments', response.data)
        self.assertIn('revenue', response.data)
        self.assertIn('services', response.data)

    def test_appointment_validation(self):
        """Test appointment validation"""
        # Test past date
        past_data = {
            **self.appointment_data,
            "start_time": (timezone.now() - timedelta(days=1)).isoformat()
        }
        response = self.client.post(
            reverse('appointment-list'),
            past_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test non-existent service
        invalid_service_data = {
            **self.appointment_data,
            "services": [99999]
        }
        response = self.client.post(
            reverse('appointment-list'),
            invalid_service_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid status update
        appointment = Appointment.objects.create(
            start_time=timezone.now() + timedelta(days=1),
            medspa=self.medspa
        )
        response = self.client.patch(
            reverse('appointment-update-status', kwargs={'pk': appointment.id}),
            {'status': 'invalid_status'},
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
