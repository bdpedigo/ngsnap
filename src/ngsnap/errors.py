class NgsnapError(Exception):
    """Base class for all ngsnap errors."""


class StateInputError(NgsnapError):
    """Raised when a Neuroglancer state input cannot be parsed or normalized."""
