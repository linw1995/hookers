import functools
from contextlib import contextmanager
from typing import Any, Generator


class Hooker:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.instance = None
        self.before_funcs = []

    def call_before(self, func):
        self.before_funcs.append(func)

        @contextmanager
        def ctx() -> Generator[None, None, None]:
            try:
                yield
            finally:
                self.before_funcs.remove(func)

        return ctx()

    def __call__(self, *args, **kwargs) -> Any:
        if self.instance:
            return self._call_with_hooks(self.instance, *args, **kwargs)
        else:
            return self._call_with_hooks(*args, **kwargs)

    def _call_with_hooks(self, *args, **kwargs) -> Any:
        for before_func in self.before_funcs:
            before_func(*args, **kwargs)

        return self.func(*args, **kwargs)

    @classmethod
    def copy_from(cls, obj) -> "Hooker":
        new_obj = cls(obj.func)
        new_obj.before_funcs = obj.before_funcs
        return new_obj

    def __get__(self, instance, cls) -> "Hooker":
        new_hooker = self.copy_from(self)
        new_hooker.instance = instance
        return new_hooker


hook = Hooker
