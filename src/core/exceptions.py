"""Core exceptions for the medical platform"""

class DatabaseError(Exception):
    """Database related errors"""
    pass

class ConfigurationError(Exception):
    """Configuration related errors"""
    pass

class ValidationError(Exception):
    """Data validation errors"""
    pass

class AuthenticationError(Exception):
    """Authentication related errors"""
    pass

class AuthorizationError(Exception):
    """Authorization related errors"""
    pass
