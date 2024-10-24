# middleware/timing_middleware.py
import time
import logging
from django.db import connection
from django.conf import settings

logger = logging.getLogger(__name__)

class TimingMiddleware:
    """
    Middleware for monitoring and logging request timing information,
    including database queries and overall response time.
    """
    
    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        # Start timing
        start_time = time.time()
        
        # Reset database query log
        if settings.DEBUG:
            initial_queries = len(connection.queries)

        # Process the request
        response = self.get_response(request)

        # Calculate timing
        duration = time.time() - start_time
        
        # Log timing information
        self.log_timing_info(request, response, duration)
        
        # Add timing headers if in debug mode
        if settings.DEBUG:
            queries_executed = len(connection.queries) - initial_queries
            response['X-Request-Duration'] = f"{duration:.3f}s"
            response['X-Queries-Count'] = str(queries_executed)
            
            # Log slow requests (over 1 second)
            if duration > 1:
                self.log_slow_request(request, duration, queries_executed)

        return response

    def log_timing_info(self, request, response, duration):
        """Log detailed timing information for the request."""
        log_data = {
            'path': request.path,
            'method': request.method,
            'duration': f"{duration:.3f}s",
            'status_code': response.status_code
        }
        
        if settings.DEBUG:
            log_data['queries'] = len(connection.queries)
            
            # Calculate time spent in database queries
            db_time = sum(float(q['time']) for q in connection.queries)
            log_data['database_time'] = f"{db_time:.3f}s"
            
            # Calculate Python processing time (excluding DB time)
            python_time = duration - db_time
            log_data['python_time'] = f"{python_time:.3f}s"
        
        logger.info(f"Request timing: {log_data}")

    def log_slow_request(self, request, duration, queries_count):
        """Log detailed information about slow requests."""
        slow_request_data = {
            'path': request.path,
            'method': request.method,
            'duration': f"{duration:.3f}s",
            'queries_count': queries_count,
            'user': str(request.user) if request.user.is_authenticated else 'anonymous'
        }
        
        if settings.DEBUG:
            # Include query information for debugging
            slow_request_data['queries'] = [
                {
                    'sql': query['sql'],
                    'time': query['time']
                }
                for query in connection.queries
            ]
        
        logger.warning(f"Slow request detected: {slow_request_data}")
