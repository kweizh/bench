from .hooks import MyHook
from my_sdk._hooks.types import Hooks

def init_hooks(hooks: Hooks):
    hooks.register_before_request_hook(MyHook())
