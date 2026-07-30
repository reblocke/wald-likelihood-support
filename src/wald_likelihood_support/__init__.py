"""Focused browser adapter for normalized Wald relative-likelihood support."""

from wald_inference import ValidationError

from .contract import calculate, calculate_json
from .models import SupportRequest, SupportResponse
from .version import __version__

__all__ = [
    "SupportRequest",
    "SupportResponse",
    "ValidationError",
    "__version__",
    "calculate",
    "calculate_json",
]
