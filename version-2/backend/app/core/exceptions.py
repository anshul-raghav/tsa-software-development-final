from fastapi import HTTPException, status


class TouchMapError(Exception):
    """Base exception for all TouchMap errors."""

    def __init__(self, message: str, detail: str | None = None):
        self.message = message
        self.detail = detail
        super().__init__(self.message)


class ScanError(TouchMapError):
    """Raised when image scanning or preprocessing fails."""
    pass


class ScanQualityError(ScanError):
    """Raised when scan quality is insufficient."""

    def __init__(self, quality_class: str, confidence: float):
        self.quality_class = quality_class
        self.confidence = confidence
        super().__init__(
            message=f"Scan quality insufficient: {quality_class}",
            detail=f"confidence={confidence:.2f}",
        )


class OCRError(TouchMapError):
    """Raised when OCR extraction fails."""
    pass


class PanelMapExtractionError(TouchMapError):
    """Raised when OpenAI PanelMap extraction fails."""
    pass


class PanelMapValidationError(TouchMapError):
    """Raised when PanelMap validation or normalization fails."""

    def __init__(self, message: str, violations: list[str] | None = None):
        self.violations = violations or []
        super().__init__(message=message, detail=str(self.violations))


class ControlGraphError(TouchMapError):
    """Raised when graph construction fails."""
    pass


class IntentParsingError(TouchMapError):
    """Raised when user intent cannot be parsed."""
    pass


class TaskPlanningError(TouchMapError):
    """Raised when a task plan cannot be generated."""
    pass


class ControlNotFoundError(TouchMapError):
    """Raised when a requested control cannot be located."""

    def __init__(self, query: str, suggestions: list[str] | None = None):
        self.query = query
        self.suggestions = suggestions or []
        super().__init__(
            message=f"Control not found: '{query}'",
            detail=f"suggestions={self.suggestions}",
        )


class GuidanceError(TouchMapError):
    """Raised when live guidance encounters an error."""
    pass


class SessionNotFoundError(TouchMapError):
    """Raised when a session or scan ID is not found."""
    pass


def touchmap_exception_to_http(error: TouchMapError) -> HTTPException:
    """Convert a domain exception to an appropriate HTTP exception."""
    status_map = {
        ScanQualityError: 422,
        PanelMapValidationError: 422,
        ControlNotFoundError: status.HTTP_404_NOT_FOUND,
        SessionNotFoundError: status.HTTP_404_NOT_FOUND,
        IntentParsingError: status.HTTP_400_BAD_REQUEST,
        OCRError: status.HTTP_502_BAD_GATEWAY,
        PanelMapExtractionError: status.HTTP_502_BAD_GATEWAY,
    }
    code = status_map.get(type(error), status.HTTP_500_INTERNAL_SERVER_ERROR)
    return HTTPException(status_code=code, detail={"message": error.message, "detail": error.detail})
