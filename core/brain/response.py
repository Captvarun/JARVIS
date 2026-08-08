from dataclasses import dataclass, field
from typing import Any, Dict, Optional

@dataclass
class StructuredResponse:
    """
    Structured response object returned by JARVIS Brain.
    """
    text: str
    intent: str = "conversation"
    success: bool = True
    action: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)
