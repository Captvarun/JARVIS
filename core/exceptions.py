class JarvisBaseException(Exception):
    """Base exception class for all JARVIS errors."""
    pass

class ServiceInitializationError(JarvisBaseException):
    """Raised when an engine service fails to initialize."""
    pass

class PluginExecutionError(JarvisBaseException):
    """Raised when a plugin execution fails."""
    pass

class UIStateError(JarvisBaseException):
    """Raised when an invalid UI state transition is requested."""
    pass
