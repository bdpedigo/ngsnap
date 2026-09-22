class NgsnapError(Exception):
    """Base class for all ngsnap errors."""


class StateInputError(NgsnapError):
    """Raised when a Neuroglancer state input cannot be parsed or normalized."""


class StateTemplateError(NgsnapError):
    """Raised when a template cannot be applied to a Neuroglancer state."""


class StyleError(NgsnapError):
    """Raised when a style cannot be loaded or is malformed."""


class RenderError(NgsnapError):
    """Raised when a render cannot be produced."""


class RenderTimeoutError(RenderError):
    """Raised when a render does not finish loading within its timeout."""
