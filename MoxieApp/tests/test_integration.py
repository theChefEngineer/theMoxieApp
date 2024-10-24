from rest_framework.test import APITestCase, APIClient
from rest_framework import status
from django.urls import reverse
from django.utils import timezone
from datetime import datetime, timedelta
import json


class TestBookingFlow(APITestCase):
    def setUp(self):
        self.client = APIClient()

        # Create a medspa
        self.medspa_data = {
            "name": "Integration Test Medspa",
            "email_address": "integration@test.com",
            "phone_number": "123-456-7890"
        }
        self.medspa_response = self.client.post(
            reverse('medspa-list'),
            self.medspa_data,
            format='json'
        )
        self.medspa_id = self.medspa_response.data['id']

        # Create category and type
        self.category_data = {
            "name": "Injectables",
            "description": "Injectable treatments"
        }
        self.category_response = self.client.post(
            reverse('servicecategory-list'),
            self.category_data,
            format='json'
        )
        self.category_id = self.category_response.data['id']

        self.type_data = {
            "name": "Neuromodulators",
            "category": self.category_id,
            "description": "Botox and similar"
        }
        self.type_response = self.client.post(
            reverse('servicetype-list'),
            self.type_data,
            format='json'
        )
        self.type_id = self.type_response.data['id']

        # Create service
        self.service_data = {
            "name": "Integration Test Service",
            "price": "299.99",
            "duration": 60,
            "medspa": self.medspa_id,
            "category": self.category_id,
            "service_type": self.type_id,
            "product": "botox",
            "supplier": "Allergan"
        }
        self.service_response = self.client.post(
            reverse('service-list'),
            self.service_data,
            format='json'
        )
        self.service_id = self.service_response.data['id']

    def test_complete_booking_flow(self):
        # 1. Get medspa availability
        tomorrow = (timezone.now() + timedelta(days=1)).strftime('%Y-%m-%d')
        availability_response = self.client.get(
            reverse('medspa-availability', kwargs={'pk': self.medspa_id}),
            {'date': tomorrow}
        )
        self.assertEqual(availability_response.status_code, status.HTTP_200_OK)

        # 2. Get available services
        services_response = self.client.get(
            f"{reverse('service-list')}?medspa_id={self.medspa_id}"
        )
        self.assertEqual(services_response.status_code, status.HTTP_200_OK)

        # 3. Create appointment
        appointment_data = {
            "start_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "medspa": self.medspa_id,
            "services": [self.service_id]
        }
        appointment_response = self.client.post(
            reverse('appointment-list'),
            appointment_data,
            format='json'
        )
        self.assertEqual(appointment_response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(appointment_response.data['total_price'], "299.99")
        self.assertEqual(appointment_response.data['total_duration'], 60)
        appointment_id = appointment_response.data['id']

        # 4. Update appointment status
        status_update_response = self.client.patch(
            reverse('appointment-update-status', kwargs={'pk': appointment_id}),
            {'status': 'completed'},
            format='json'
        )
        self.assertEqual(status_update_response.status_code, status.HTTP_200_OK)
        self.assertEqual(status_update_response.data['status'], 'completed')

        # 5. Verify medspa statistics
        stats_response = self.client.get(
            reverse('medspa-statistics', kwargs={'pk': self.medspa_id})
        )
        self.assertEqual(stats_response.status_code, status.HTTP_200_OK)
        self.assertEqual(stats_response.data['total_appointments'], 1)

    def test_invalid_booking_scenarios(self):
        # Test booking with past date
        past_appointment_data = {
            "start_time": (timezone.now() - timedelta(days=1)).isoformat(),
            "medspa": self.medspa_id,
            "services": [self.service_id]
        }
        response = self.client.post(
            reverse('appointment-list'),
            past_appointment_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test booking with non-existent service
        invalid_service_data = {
            "start_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "medspa": self.medspa_id,
            "services": [9999]
        }
        response = self.client.post(
            reverse('appointment-list'),
            invalid_service_data,
            format='json'
        )
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

        # Test invalid status update
        appointment_data = {
            "start_time": (timezone.now() + timedelta(days=1)).isoformat(),
            "medspa": self.medspa_id,
            "services": [self.service_id]
        }
        appointment_response = self.client.post(
            reverse('appointment-list'),
            appointment_data,
            format='json'
        )
        appointment_id = appointment_response.data['id']

        invalid_status_response = self.client.patch(
            reverse('appointment-update-status', kwargs={'pk': appointment_id}),
            {'status': 'invalid_status'},
            format='json'
        )
        self.assertEqual(invalid_status_response.status_code, status.HTTP_400_BAD_REQUEST)
