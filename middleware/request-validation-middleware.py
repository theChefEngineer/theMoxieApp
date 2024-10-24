# middleware/request_validation.py
import json
from django.http import JsonResponse
from rest_framework import status
from django.urls import resolve
import logging

logger = logging.getLogger(__name__)

class RequestValidationMiddleware:
    """
    Middleware for validating incoming requests, including content type,
    payload size, and required headers.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response
        self.max_content_length = 10 * 1024 * 1024  # 10MB

    def __call__(self, request):
        # Skip validation for non-API paths
        if not request.path.startswith('/api/'):
            return self.get_response(request)

        # Validate request
        validation_result = self.validate_request(request)
        if validation_result:
            return validation_result

        return self.get_response(request)

    def validate_request(self, request):
        """Validate various aspects of the incoming request."""
        # Validate content type for POST/PUT/PATCH requests
        if request.method in ['POST', 'PUT', 'PATCH']:
            content_type = request.headers.get('Content-Type', '')
            if not content_type.startswith('application/json'):
                return JsonResponse({
                    'error': 'Invalid Content-Type',
                    'detail': 'Request must be application/json'
                }, status=status.HTTP_415_UNSUPPORTED_MEDIA_TYPE)

            # Validate content length
            if request.META.get('CONTENT_LENGTH'):
                content_length = int(request.META['CONTENT_LENGTH'])
                if content_length > self.max_content_length:
                    return JsonResponse({
                        'error': 'Payload Too Large',
                        'detail': f'Request payload must not exceed {self.max_content_length} bytes'
                    }, status=status.HTTP_413_REQUEST_ENTITY_TOO_LARGE)

            # Validate JSON payload
            try:
                if request.body:
                    json.loads(request.body)
            except json.JSONDecodeError:
                return JsonResponse({
                    'error': 'Invalid JSON',
                    'detail': 'Request body must be valid JSON'
                }, status=status.HTTP_400_BAD_REQUEST)

        # Validate required headers
        required_headers = self.get_required_headers(request)
        missing_headers = [header for header in required_headers 
                         if header not in request.headers]
        if missing_headers:
            return JsonResponse({
                'error': 'Missing Required Headers',
                'detail': f'The following headers are required: {", ".join(missing_headers)}'
            }, status=status.HTTP_400_BAD_REQUEST)

        return None

    def get_required_headers(self, request):
        """Determine required headers based on the request path and method."""
        required_headers = []
        
        # Add Authorization header for protected endpoints
        if not request.path.startswith(('/api/token/', '/api/public/')):
            required_headers.append('Authorization')

        return required_headers
