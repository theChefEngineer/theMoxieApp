# utils/decorators.py
import logging
import time
import functools
from django.core.cache import cache
from django.db import transaction
from rest_framework.response import Response
from rest_framework import status
from .custom_exceptions import ValidationError

logger = logging.getLogger(__name__)


def handle_exceptions(func):
    """Decorator for handling exceptions in view methods."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        try:
            return func(*args, **kwargs)
        except ValidationError as e:
            logger.warning(f"Validation error in {func.__name__}: {str(e)}")
            return Response(
                {'error': str(e)},
                status=status.HTTP_400_BAD_REQUEST
            )
        except Exception as e:
            logger.error(f"Error in {func.__name__}: {str(e)}", exc_info=True)
            return Response(
                {'error': 'Internal server error'},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )

    return wrapper


def measure_execution_time(func):
    """Decorator for measuring and logging execution time."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        start_time = time.time()
        result = func(*args, **kwargs)
        duration = time.time() - start_time

        logger.info(
            f"Function {func.__name__} took {duration:.3f} seconds to execute"
        )

        # Add timing header to response if it's a Response object
        if isinstance(result, Response):
            result['X-Execution-Time'] = f"{duration:.3f}s"

        return result

    return wrapper


def cache_response(timeout=300):
    """Decorator for caching view responses."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            # Generate cache key
            cache_key = f"{func.__name__}:{args}:{kwargs}"

            # Try to get from cache
            cached_response = cache.get(cache_key)
            if cached_response is not None:
                return cached_response

            # Get fresh response
            response = func(*args, **kwargs)

            # Cache the response
            if response.status_code == 200:
                cache.set(cache_key, response, timeout)

            return response

        return wrapper

    return decorator


def atomic_transaction(func):
    """Decorator for wrapping views in atomic transactions."""

    @functools.wraps(func)
    def wrapper(*args, **kwargs):
        with transaction.atomic():
            return func(*args, **kwargs)

    return wrapper


def validate_request_data(*required_fields):
    """Decorator for validating required request data fields."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            if request.method in ['POST', 'PUT', 'PATCH']:
                missing_fields = [
                    field for field in required_fields
                    if field not in request.data
                ]
                if missing_fields:
                    return Response(
                        {
                            'error': 'Missing required fields',
                            'fields': missing_fields
                        },
                        status=status.HTTP_400_BAD_REQUEST
                    )
            return func(view_instance, request, *args, **kwargs)

        return wrapper

    return decorator


def require_permissions(*permissions):
    """Decorator for checking required permissions."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            for permission in permissions:
                if not request.user.has_perm(permission):
                    return Response(
                        {'error': f'Missing required permission: {permission}'},
                        status=status.HTTP_403_FORBIDDEN
                    )
            return func(view_instance, request, *args, **kwargs)

        return wrapper

    return decorator


def rate_limit(calls=100, period=3600):
    """Decorator for rate limiting view methods."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(view_instance, request, *args, **kwargs):
            # Generate rate limit key
            key = f"rate_limit:{request.user.id}:{func.__name__}"

            # Get current count
            count = cache.get(key, 0)

            if count >= calls:
                return Response(
                    {'error': 'Rate limit exceeded'},
                    status=status.HTTP_429_TOO_MANY_REQUESTS
                )

            # Increment count
            cache.set(key, count + 1, period)

            return func(view_instance, request, *args, **kwargs)

        return wrapper

    return decorator


def log_action(action_name):
    """Decorator for logging view actions."""

    def decorator(func):
        @functools.wraps(func)
        def wrapper(*args, **kwargs):
            logger.info(f"Action {action_name} started")
            try:
                result = func(*args, **kwargs)
                logger.info(f"Action {action_name} completed successfully")
                return result
            except Exception as e:
                logger.error(
                    f"Action {action_name} failed: {str(e)}",
                    exc_info=True
                )
                raise

        return wrapper

    return decorator
