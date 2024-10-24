from datetime import datetime, timedelta


def create_test_data(self):
    """Helper method to create test data for all tests."""
    self.medspa = self.medspa_model.objects.create(
        name="Test Medspa",
        email_address="test@medspa.com",
        phone_number="123-456-7890"
    )

    self.service = self.service_model.objects.create(
        name="Test Service",
        description="Test Description",
        price="199.99",
        duration=60,
        medspa=self.medspa,
        category="injectables",
        service_type="neuromodulators",
        product="botox"
    )
