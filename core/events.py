from PySide6.QtCore import QObject, Signal

class EventBus(QObject):
    """
    Central Event Bus for JARVIS.
    Decouples UI components from background services (AI, Voice, Vision, etc.)
    """
    # System events
    system_status_changed = Signal(str)  # Status message
    log_emitted = Signal(str, str)        # Level, Message
    
    # User interaction events
    user_command_submitted = Signal(str) # Command text
    
    # Service response events
    ai_response_received = Signal(str)   # Response text
    voice_state_changed = Signal(str)    # Listening, Processing, Speaking, Idle
    vision_state_changed = Signal(str)   # Standby, Analyzing, Ready
    vision_frame_processed = Signal(object) # Frame data or detection info
    
    # State update events
    state_updated = Signal(str, object)  # Key, Value

# Global singleton event bus
events = EventBus()
