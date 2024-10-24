# utils/custom_exceptions.py

class ServiceValidationError(Exception):
    """Exception raised for validation errors in Service operations."""
    pass

class AppointmentValidationError(Exception):
    """Exception raised for validation errors in Appointment operations."""
    pass

class MedspaValidationError(Exception):
    """Exception raised for validation errors in Medspa operations."""
    pass

class ServiceNotFoundError(Exception):
    """Exception raised when a requested Service is not found."""
    pass

class InvalidStatusError(Exception):
    """Exception raised when an invalid status is provided."""
    pass

class ConcurrentBookingError(Exception):
    """Exception raised when there's a concurrent booking conflict."""
    pass

class RateLimitExceededError(Exception):
    """Exception raised when rate limit is exceeded."""
    pass

class ResourceConflictError(Exception):
    """Exception raised when there's a conflict in resource operations."""
    pass

class InvalidPayloadError(Exception):
    """Exception raised when request payload is invalid."""
    pass

class DatabaseIntegrityError(Exception):
    """Exception raised for database integrity violations."""
    pass
