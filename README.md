# Moxie Medspa Management System

## Overview
This is a Django REST API for managing medspa services and appointments. The system allows for creating and managing medspas, their services, and customer appointments.

## Prerequisites
- Python 3.11+
- PostgreSQL
- Redis
- Docker and Docker Compose (optional)

## Installation

### Using Docker
1. Clone the repository:
```bash
git clone <repository-url>
cd MoxieApp
```

2. Build and run the containers:
```bash
docker-compose up --build
```

### Manual Setup
1. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

2. Install dependencies:
```bash
pip install -r requirements.txt
```

3. Set up the database:
```bash
python manage.py migrate
```

4. Run the development server:
```bash
python manage.py runserver
```

## API Endpoints

### Medspa Endpoints
- `GET /api/medspas/` - List all medspas
- `POST /api/medspas/` - Create a new medspa
- `GET /api/medspas/{id}/` - Retrieve a specific medspa
- `PUT /api/medspas/{id}/` - Update a medspa
- `DELETE /api/medspas/{id}/` - Delete a medspa

### Service Endpoints
- `GET /api/services/` - List all services
- `POST /api/services/` - Create a new service
- `GET /api/services/{id}/` - Retrieve a specific service
- `PUT /api/services/{id}/` - Update a service
- `DELETE /api/services/{id}/` - Delete a service

### Appointment Endpoints
- `GET /api/appointments/` - List all appointments
- `POST /api/appointments/` - Create a new appointment
- `GET /api/appointments/{id}/` - Retrieve a specific appointment
- `PUT /api/appointments/{id}/` - Update an appointment
- `PATCH /api/appointments/{id}/update_status/` - Update appointment status

## Documentation
- Swagger UI: `/swagger/`
- ReDoc: `/redoc/`

## Testing
Run the test suite:
```bash
pytest
```

## Linting
Run linting checks:
```bash
flake8
black .
isort .
```

## License
[License Information]
