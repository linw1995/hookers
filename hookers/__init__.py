import ctypes
from contextlib import ExitStack, contextmanager
from functools import partial
from inspect import currentframe
from types import FrameType
from typing import Any, Dict, Generator, Optional


@contextmanager
def _temporary_replace(scope: Dict[str, Any], target: Any, new: Any):
    keys = []
    for key, value in scope.items():
        if value is not target:
            continue
        keys.append(key)

    try:
        for key in keys:
            scope[key] = new

        yield
    finally:
        for key in keys:
            scope[key] = target


def _apply_frame_change(frame: FrameType):
    ctypes.pythonapi.PyFrame_LocalsToFast(ctypes.py_object(frame), ctypes.c_int(0))


@contextmanager
def _temporary_replace_scope_from_frame(frame: FrameType, target: Any, new: Any):
    try:
        replacer = partial(_temporary_replace, target=target, new=new)
        with ExitStack() as stack:
            stack.enter_context(replacer(frame.f_locals))
            stack.enter_context(replacer(frame.f_globals))
            _apply_frame_change(frame)
            yield
    finally:
        _apply_frame_change(frame)


class Hooker:
    def __init__(self, func):
        self.func = func
        self.original = None
        self.before_funcs = []

    def call_before(self, func):
        self.before_funcs.append(func)

        @contextmanager
        def ctx():
            try:
                yield
            finally:
                self.before_funcs.remove(func)

        return ctx()

    def call_with_hooks(self, *args, **kwargs):
        if not self.hooking:
            raise RuntimeError("Hooker is not hooking")

        for before_func in self.before_funcs:
            before_func(*args, **kwargs)

        return self.func(*args, **kwargs)

    @contextmanager
    def hook(self, frame: FrameType):
        try:
            self.hooking = True
            with _temporary_replace_scope_from_frame(
                frame=frame, target=self.func, new=self.call_with_hooks
            ):
                yield
        finally:
            self.hooking = False


def getframe(depth: int = 0) -> Optional[FrameType]:
    frame = currentframe()
    if frame is None:
        # If running in an implementation without Python stack frame support,
        return None

    while frame and depth > -1:
        frame = frame.f_back
        depth -= 1

    return frame


@contextmanager
def hook(func) -> Generator[Hooker, None, None]:
    frame = getframe(depth=2)
    if not isinstance(frame, FrameType):
        raise RuntimeError("Cannot hook without frame.")

    hooker = Hooker(func)
    with hooker.hook(frame):
        yield hooker
