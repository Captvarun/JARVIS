from enum import Enum
from core.logger import logger

class LifecycleState(Enum):
    UNINITIALIZED = "UNINITIALIZED"
    INITIALIZING = "INITIALIZING"
    INITIALIZED = "INITIALIZED"
    STARTING = "STARTING"
    RUNNING = "RUNNING"
    PAUSING = "PAUSING"
    PAUSED = "PAUSED"
    STOPPING = "STOPPING"
    STOPPED = "STOPPED"
    SHUTTING_DOWN = "SHUTTING_DOWN"
    SHUTDOWN = "SHUTDOWN"
    ERROR = "ERROR"

class BaseLifecycleComponent:
    """
    Standard Base Class for all JARVIS Engine Services & Plugins.
    Enforces the unified lifecycle state machine:
    Initialize -> Start -> Running -> Paused -> Stopped -> Shutdown
    """
    def __init__(self, name: str):
        self.name = name
        self.state = LifecycleState.UNINITIALIZED

    def initialize(self) -> bool:
        """Phase 1: Setup resources, configurations, and connections."""
        logger.info(f"[{self.name}] Transitioning: {self.state.value} -> INITIALIZING")
        self.state = LifecycleState.INITIALIZING
        try:
            if self.on_initialize():
                self.state = LifecycleState.INITIALIZED
                logger.info(f"[{self.name}] State: INITIALIZED")
                return True
        except Exception as e:
            logger.error(f"[{self.name}] Initialization Error: {e}")
            self.state = LifecycleState.ERROR
        return False

    def start(self) -> bool:
        """Phase 2: Transition from Initialized/Stopped to Running."""
        if self.state not in (LifecycleState.INITIALIZED, LifecycleState.STOPPED):
            logger.warning(f"[{self.name}] Cannot start from state {self.state.value}")
            return False
        logger.info(f"[{self.name}] Transitioning: {self.state.value} -> STARTING")
        self.state = LifecycleState.STARTING
        try:
            if self.on_start():
                self.state = LifecycleState.RUNNING
                logger.info(f"[{self.name}] State: RUNNING")
                return True
        except Exception as e:
            logger.error(f"[{self.name}] Start Error: {e}")
            self.state = LifecycleState.ERROR
        return False

    def pause(self) -> bool:
        """Phase 3: Pause execution without tearing down resources."""
        if self.state != LifecycleState.RUNNING:
            return False
        self.state = LifecycleState.PAUSING
        try:
            if self.on_pause():
                self.state = LifecycleState.PAUSED
                logger.info(f"[{self.name}] State: PAUSED")
                return True
        except Exception as e:
            logger.error(f"[{self.name}] Pause Error: {e}")
            self.state = LifecycleState.ERROR
        return False

    def resume(self) -> bool:
        """Resume from Paused -> Running."""
        if self.state != LifecycleState.PAUSED:
            return False
        return self.start()

    def stop(self) -> bool:
        """Phase 4: Stop active threads/workers while retaining initialized handles."""
        if self.state not in (LifecycleState.RUNNING, LifecycleState.PAUSED):
            return False
        self.state = LifecycleState.STOPPING
        try:
            if self.on_stop():
                self.state = LifecycleState.STOPPED
                logger.info(f"[{self.name}] State: STOPPED")
                return True
        except Exception as e:
            logger.error(f"[{self.name}] Stop Error: {e}")
            self.state = LifecycleState.ERROR
        return False

    def shutdown(self) -> bool:
        """Phase 5: Release memory, close file descriptors, and terminate."""
        logger.info(f"[{self.name}] Transitioning to SHUTTING_DOWN")
        self.state = LifecycleState.SHUTTING_DOWN
        try:
            self.on_shutdown()
            self.state = LifecycleState.SHUTDOWN
            logger.info(f"[{self.name}] State: SHUTDOWN")
            return True
        except Exception as e:
            logger.error(f"[{self.name}] Shutdown Error: {e}")
            self.state = LifecycleState.ERROR
        return False

    # Virtual Hooks to be overridden by Services & Plugins
    def on_initialize(self) -> bool:
        return True

    def on_start(self) -> bool:
        return True

    def on_pause(self) -> bool:
        return True

    def on_stop(self) -> bool:
        return True

    def on_shutdown(self) -> None:
        pass
