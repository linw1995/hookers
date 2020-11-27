import ctypes
import sys
from contextlib import ExitStack, contextmanager
from functools import partial
from inspect import currentframe
from pathlib import Path
from types import FrameType
from typing import Any, Callable, Dict, Generator, Optional


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
        self.before_funcs = []
        self._current_file_path = Path(currentframe().f_code.co_filename)

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

    def trace_func(
        self, frame: FrameType, event: str, arg: Any
    ) -> Optional[Callable[[FrameType, str, Any], Any]]:
        assert event == "call"
        if not self.hooking:
            sys.settrace(None)

        file_path = Path(frame.f_code.co_filename)
        if file_path == self._current_file_path:
            return None

        ctx = _temporary_replace_scope_from_frame(
            frame=frame, target=self.func, new=self.call_with_hooks
        )

        def ctx_exit_after_return(frame: FrameType, event: str, arg: Any) -> None:
            if event != "return":
                return None

            ctx.__exit__(None, None, None)

        ctx.__enter__()
        return ctx_exit_after_return

    @contextmanager
    def hook(self, frame: FrameType):
        try:
            self.hooking = True
            with _temporary_replace_scope_from_frame(
                frame=frame, target=self.func, new=self.call_with_hooks
            ):
                sys.settrace(self.trace_func)
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
