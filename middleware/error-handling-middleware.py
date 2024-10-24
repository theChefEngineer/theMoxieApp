# middleware/error_handling.py
import logging
import traceback
import json
from django.http import JsonResponse
from rest_framework import status
from django.core.exceptions import ValidationError
from django.db.utils import IntegrityError

logger = logging.getLogger(__name__)

class ErrorHandlingMiddleware:
    """
    Middleware for handling various types of exceptions and converting them
    to appropriate JSON responses with proper status codes.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        try:
            response = self.get_response(request)
            return response
        except Exception as e:
            return self.handle_exception(e)

    def handle_exception(self, exc):
        """Handle different types of exceptions and return appropriate responses."""
        if isinstance(exc, ValidationError):
            return self.handle_validation_error(exc)
        elif isinstance(exc, IntegrityError):
            return self.handle_integrity_error(exc)
        elif isinstance(exc, json.JSONDecodeError):
            return self.handle_json_error(exc)
        else:
            return self.handle_unknown_error(exc)

    def handle_validation_error(self, exc):
        logger.warning(f"Validation error: {str(exc)}")
        return JsonResponse({
            'error': 'Validation Error',
            'detail': str(exc),
            'type': 'validation_error'
        }, status=status.HTTP_400_BAD_REQUEST)

    def handle_integrity_error(self, exc):
        logger.error(f"Database integrity error: {str(exc)}")
        return JsonResponse({
            'error': 'Data Integrity Error',
            'detail': 'The operation could not be completed due to a data conflict',
            'type': 'integrity_error'
        }, status=status.HTTP_409_CONFLICT)

    def handle_json_error(self, exc):
        logger.warning(f"JSON decode error: {str(exc)}")
        return JsonResponse({
            'error': 'Invalid JSON',
            'detail': 'The request contains invalid JSON data',
            'type': 'json_error'
        }, status=status.HTTP_400_BAD_REQUEST)

    def handle_unknown_error(self, exc):
        logger.error(f"Unexpected error: {str(exc)}\n{traceback.format_exc()}")
        return JsonResponse({
            'error': 'Internal Server Error',
            'detail': 'An unexpected error occurred',
            'type': 'server_error'
        }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
