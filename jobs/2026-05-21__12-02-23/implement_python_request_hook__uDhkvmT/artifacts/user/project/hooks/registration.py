from .hooks import MyHook
from .._hooks.types import Hooks

def init_hooks(hooks: Hooks):
    hooks.register_before_request_hook(MyHook())
