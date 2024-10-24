from django.test import TestCase
from django.core.exceptions import ValidationError
from datetime import datetime, timedelta
from decimal import Decimal
from ..models import (
    Medspa,
    Service,
    Appointment,
    ServiceCategory,
    ServiceType,
    AppointmentService
)

class TestMedspaModel(TestCase):
    def setUp(self):
        self.medspa = Medspa.objects.create(
            name="Test Medspa",
            email_address="test@medspa.com",
            phone_number="123-456-7890",
            address="123 Test St"
        )

    def test_medspa_creation(self):
        self.assertTrue(isinstance(self.medspa, Medspa))
        self.assertEqual(str(self.medspa), "Test Medspa")

    def test_unique_email(self):
        with self.assertRaises(ValidationError):
            Medspa.objects.create(
                name="Another Medspa",
                email_address="test@medspa.com"  # Duplicate email
            )

    def test_phone_number_cleaning(self):
        medspa = Medspa.objects.create(
            name="Phone Test",
            email_address="phone@test.com",
            phone_number="(123) 456-7890"
        )
        self.assertEqual(medspa.phone_number, "1234567890")

class TestServiceCategoryModel(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(
            name="Injectables",
            description="Injectable treatments"
        )

    def test_category_creation(self):
        self.assertTrue(isinstance(self.category, ServiceCategory))
        self.assertEqual(str(self.category), "Injectables")

class TestServiceTypeModel(TestCase):
    def setUp(self):
        self.category = ServiceCategory.objects.create(name="Injectables")
        self.service_type = ServiceType.objects.create(
            category=self.category,
            name="Neuromodulators",
            description="Botox and similar treatments"
        )

    def test_service_type_creation(self):
        self.assertTrue(isinstance(self.service_type, ServiceType))
        self.assertEqual(
            str(self.service_type),
            "Injectables - Neuromodulators"
        )

class TestServiceModel(TestCase):
    def setUp(self):
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
            name="Botox",
            description="Anti-wrinkle treatment",
            price=Decimal("299.99"),
            duration=30,
            medspa=self.medspa,
            category=self.category,
            service_type=self.service_type,
            product="Botox",
            supplier="Allergan"
        )

    def test_service_creation(self):
        self.assertTrue(isinstance(self.service, Service))
        self.assertEqual(str(self.service), "Test Medspa - Botox")

    def test_service_price_validation(self):
        with self.assertRaises(ValidationError):
            Service.objects.create(
                name="Invalid Price Service",
                price=Decimal("-100"),
                duration=30,
                medspa=self.medspa,
                category=self.category,
                service_type=self.service_type
            )

    def test_service_type_category_validation(self):
        wrong_category = ServiceCategory.objects.create(name="Facials")
        with self.assertRaises(ValidationError):
            Service.objects.create(
                name="Invalid Category Service",
                price=Decimal("100"),
                duration=30,
                medspa=self.medspa,
                category=wrong_category,
                service_type=self.service_type  # Type belongs to different category
            )

class TestAppointmentModel(TestCase):
    def setUp(self):
        self.medspa = Medspa.objects.create(
            name="Test Medspa",
            email_address="test@medspa.com"
        )
        self.category = ServiceCategory.objects.create(name="Injectables")
        self.service_type = ServiceType.objects.create(
            category=self.category,
            name="Neuromodulators"
        )
        self.service1 = Service.objects.create(
            name="Botox",
            price=Decimal("299.99"),
            duration=30,
            medspa=self.medspa,
            category=self.category,
            service_type=self.service_type
        )
        self.service2 = Service.objects.create(
            name="Facial",
            price=Decimal("199.99"),
            duration=60,
            medspa=self.medspa,
            category=self.category,
            service_type=self.service_type
        )
        self.appointment = Appointment.objects.create(
            start_time=datetime.now() + timedelta(days=1),
            medspa=self.medspa
        )
        self.appointment.services.add(self.service1, self.service2)

    def test_appointment_creation(self):
        self.assertTrue(isinstance(self.appointment, Appointment))
        self.assertEqual(self.appointment.services.count(), 2)

    def test_total_duration(self):
        self.assertEqual(self.appointment.total_duration, 90)

    def test_total_price(self):
        self.assertEqual(
            self.appointment.total_price,
            Decimal("499.98")
        )

    def test_past_appointment_validation(self):
        with self.assertRaises(ValidationError):
            Appointment.objects.create(
                start_time=datetime.now() - timedelta(days=1),
                medspa=self.medspa
            )

    def test_status_update(self):
        self.appointment.status = 'completed'
        self.appointment.save()
        self.assertEqual(self.appointment.status, 'completed')

    def test_invalid_status(self):
        with self.assertRaises(ValidationError):
            self.appointment.status = 'invalid_status'
            self.appointment.save()
