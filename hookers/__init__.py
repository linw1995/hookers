import asyncio
import functools
import weakref
from contextlib import contextmanager
from typing import Any, Generator, List


class Func:
    def __init__(self, func):
        functools.update_wrapper(self, func)
        self.func = func
        self.is_async_func = asyncio.iscoroutinefunction(func)

    def __call__(self, *args, **kwargs) -> Any:
        return self.func(*args, **kwargs)


class Hooker(Func):
    def __init__(self, func):
        super().__init__(func)

        self.instance = None
        self.before_funcs: List[Func] = []
        self.after_funcs: List[Func] = []
        self.decorators: List[Func] = []

        self._instance2hooker = weakref.WeakKeyDictionary()

    def _validate_hook(self, func: Func):
        if func.is_async_func and not self.is_async_func:
            raise ValueError("Cannot hook an un-async function with an async function")

    def call_before(self, func):
        func = Func(func)
        self._validate_hook(func)
        self.before_funcs.append(func)

        @contextmanager
        def ctx() -> Generator[None, None, None]:
            try:
                yield
            finally:
                self.before_funcs.remove(func)

        return ctx()

    def call_after(self, func):
        func = Func(func)
        self._validate_hook(func)
        self.after_funcs.append(func)

        @contextmanager
        def ctx() -> Generator[None, None, None]:
            try:
                yield
            finally:
                self.after_funcs.remove(func)

        return ctx()

    def decorated_by(self, func):
        # TODO: need more validations of paramater "func"
        func = Func(func)
        if func.is_async_func:
            raise ValueError("The decorator must be an un-async function")

        self.decorators.append(func)

        @contextmanager
        def ctx() -> Generator[None, None, None]:
            try:
                yield
            finally:
                self.decorators.remove(func)

        return ctx()

    @property
    def decorated_func(self):
        func = self.func
        for decorator in self.decorators:
            func = decorator(func)

        return func

    def __call__(self, *args, **kwargs) -> Any:
        if self.is_async_func:
            caller = self._async_call_with_hooks
        else:
            caller = self._call_with_hooks

        if self.instance:
            return caller(self.instance, *args, **kwargs)
        else:
            return caller(*args, **kwargs)

    def _call_with_hooks(self, *args, **kwargs) -> Any:
        for before_func in self.before_funcs:
            before_func(*args, **kwargs)

        rv = self.decorated_func(*args, **kwargs)

        for after_func in self.after_funcs:
            after_func(rv)

        return rv

    async def _async_call_with_hooks(self, *args, **kwargs) -> Any:
        for before_func in self.before_funcs:
            if before_func.is_async_func:
                await before_func(*args, **kwargs)
            else:
                before_func(*args, **kwargs)

        rv = await self.func(*args, **kwargs)

        for after_func in self.after_funcs:
            if after_func.is_async_func:
                await after_func(rv)
            else:
                after_func(rv)

        return rv

    @classmethod
    def copy_from(cls, obj) -> "Hooker":
        new_obj = cls(obj.func)
        new_obj.before_funcs = obj.before_funcs.copy()
        new_obj._instance2hooker = obj._instance2hooker
        return new_obj

    def __get__(self, instance, cls) -> "Hooker":
        """
        Implement the `__get__` method of descriptor protocol
        for decorating the class method.
        """
        if instance is None:
            # Unbound method
            return self

        # bound method
        if instance not in self._instance2hooker:
            # first time to access
            new_hooker = self.copy_from(self)
            new_hooker.instance = instance
            self._instance2hooker[instance] = new_hooker

        return self._instance2hooker[instance]


hook = Hooker
