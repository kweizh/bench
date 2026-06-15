"""Hook registration — wire custom hooks into the SDK hook registry."""

from .custom_hooks import OrganizationIdHook
from .sdkhooks import SDKHooks


def register_hooks(hooks: SDKHooks) -> None:
    """Register all custom hooks with the provided SDKHooks instance."""
    hooks.register_before_request_hook(OrganizationIdHook())
