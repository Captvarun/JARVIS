from core.lifecycle import BaseLifecycleComponent

class VoiceService(BaseLifecycleComponent):
    """Voice Subsystem Engine Component."""
    def __init__(self):
        super().__init__("VoiceService")

    def on_initialize() -> bool:
        return True

    def on_start() -> bool:
        return True

    def on_stop() -> bool:
        return True
