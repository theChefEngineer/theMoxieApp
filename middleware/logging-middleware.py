# middleware/logging_middleware.py
import logging
import time
import json
from django.utils import timezone
from django.conf import settings
import uuid

logger = logging.getLogger(__name__)

class LoggingMiddleware:
    """
    Middleware for logging detailed information about requests and responses,
    including timing, payload information, and status codes.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        request.id = str(uuid.uuid4())
        request.start_time = time.time()
        
        # Log the incoming request
        self.log_request(request)
        
        response = self.get_response(request)
        
        # Log the response
        self.log_response(request, response)
        
        return response

    def log_request(self, request):
        """Log details about the incoming request."""
        try:
            payload = None
            if request.body:
                payload = json.loads(request.body)
            
            log_data = {
                'request_id': request.id,
                'timestamp': timezone.now().isoformat(),
                'method': request.method,
                'path': request.path,
                'query_params': dict(request.GET),
                'payload': payload,
                'user': str(request.user) if request.user.is_authenticated else 'anonymous',
                'ip': self.get_client_ip(request)
            }
            
            logger.info(f"Incoming request: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Error logging request: {str(e)}")

    def log_response(self, request, response):
        """Log details about the outgoing response."""
        try:
            duration = time.time() - request.start_time
            
            log_data = {
                'request_id': request.id,
                'status_code': response.status_code,
                'duration': f"{duration:.3f}s",
                'content_length': len(response.content) if hasattr(response, 'content') else 0
            }
            
            logger.info(f"Outgoing response: {json.dumps(log_data)}")
            
        except Exception as e:
            logger.error(f"Error logging response: {str(e)}")

    def get_client_ip(self, request):
        """Extract the client IP address from the request."""
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            return x_forwarded_for.split(',')[0]
        return request.META.get('REMOTE_ADDR')
