import pytest

from hookers import hook


def test_hook_func_call_before():
    @hook
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    inputs = []

    def dump_input(*args, **kwargs):
        inputs.append((args, kwargs))

    hello.call_before(dump_input)

    assert hello(*args, **kwargs) == rv
    assert inputs == [(args, kwargs)]


def test_hook_func_call_after():
    @hook
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    outputs = []

    def dump_output(rv):
        outputs.append(rv)

    hello.call_after(dump_output)

    assert hello(*args, **kwargs) == rv
    assert outputs == [rv]


def test_temporary_hook_func_call_before():
    @hook
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    inputs = []

    def dump_input(*args, **kwargs):
        inputs.append((args, kwargs))

    with hello.call_before(dump_input):
        assert hello(*args, **kwargs) == rv
        assert inputs == [(args, kwargs)]

    assert hello(*args, **kwargs) == rv
    assert inputs == [(args, kwargs)]


def test_temporary_hook_func_call_after():
    @hook
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    outputs = []

    def dump_output(rv):
        outputs.append(rv)

    with hello.call_after(dump_output):
        assert hello(*args, **kwargs) == rv
        assert outputs == [rv]

    assert hello(*args, **kwargs) == rv
    assert outputs == [rv]


def test_hook_obj_method():
    class Person:
        @hook
        def hello(self, name):
            return f"hello {name}"

    person = Person()
    args = ("world",)
    kwargs = {}
    rv = "hello world"

    inputs = []

    def dump_input(self, *args, **kwargs):
        inputs.append((self, args, kwargs))

    with person.hello.call_before(dump_input):
        assert person.hello(*args, **kwargs) == rv
        assert inputs == [(person, args, kwargs)]


def test_hook_obj_method_isolatively():
    class Person:
        @hook
        def hello(self, name):
            return f"hello {name}"

    jack = Person()
    salra = Person()

    inputs = []

    def dump_input(self, *args, **kwargs):
        inputs.append((self, args, kwargs))

    with jack.hello.call_before(dump_input):
        assert jack.hello("salra") == "hello salra"
        assert inputs == [(jack, ("salra",), {})]

        assert salra.hello("jack") == "hello jack"
        assert inputs == [(jack, ("salra",), {})]


def test_obj_hooked_method_got_overwrited():
    class Person:
        @hook
        def hello(self, name):
            return f"hello {name}"

    person = Person()

    def assert_not_called(self, *args, **kwargs):
        assert 0

    person.hello.call_before(assert_not_called)
    person.hello = lambda x: f"hello {x}"
    assert isinstance(Person.hello, hook)
    assert person.hello("world") == "hello world"


def test_hook_func_call_before_with_async_func():
    @hook
    def hello(name):
        return f"hello {name}"

    async def async_hook():
        pass

    with pytest.raises(ValueError):
        hello.call_before(async_hook)


@pytest.mark.asyncio
async def test_hook_async_func_call_before():
    @hook
    async def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    inputs = []

    def dump_input(*args, **kwargs):
        inputs.append((args, kwargs))

    hello.call_before(dump_input)

    assert await hello(*args, **kwargs) == rv
    assert inputs == [(args, kwargs)]


@pytest.mark.asyncio
async def test_hook_async_func_call_after():
    @hook
    async def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    outputs = []

    def dump_output(rv):
        outputs.append(rv)

    hello.call_after(dump_output)

    assert await hello(*args, **kwargs) == rv
    assert outputs == [rv]


@pytest.mark.asyncio
async def test_hook_async_func_call_before_with_async_func():
    @hook
    async def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    inputs = []

    async def dump_input(*args, **kwargs):
        inputs.append((args, kwargs))

    hello.call_before(dump_input)

    assert await hello(*args, **kwargs) == rv
    assert inputs == [(args, kwargs)]


@pytest.mark.asyncio
async def test_hook_async_func_call_after_with_async_func():
    @hook
    async def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    outputs = []

    async def dump_output(rv):
        outputs.append(rv)

    hello.call_after(dump_output)

    assert await hello(*args, **kwargs) == rv
    assert outputs == [rv]


def test_hook_func_with_decorator():
    @hook
    def hello(name):
        return f"hello {name}"

    results = []

    def dump_invocation(func):
        def wrap(*args, **kwargs):
            rv = func(*args, **kwargs)
            results.append((args, kwargs, rv))
            return rv

        return wrap

    hello.decorated_by(dump_invocation)

    assert hello("world") == "hello world"
    assert results == [(("world",), {}, "hello world")]


def test_temporary_hook_func_with_decorator():
    @hook
    def hello(name):
        return f"hello {name}"

    results = []

    def dump_invocation(func):
        def wrap(*args, **kwargs):
            rv = func(*args, **kwargs)
            results.append((args, kwargs, rv))
            return rv

        return wrap

    with hello.decorated_by(dump_invocation):
        assert hello("world") == "hello world"
        assert results == [(("world",), {}, "hello world")]

    assert hello("world") == "hello world"
    assert results == [(("world",), {}, "hello world")]


def test_hook_with_invalid_decorator():
    @hook
    def hello(name):
        return f"hello {name}"

    with pytest.raises(ValueError):

        async def boo(func):
            pass

        hello.decorated_by(boo)


def test_hook_func_with_decorators():
    @hook
    def hello(name):
        return f"hello {name}"

    inputs = []
    outputs = []

    def dump_input(func):
        def wrap(*args, **kwargs):
            rv = func(*args, **kwargs)
            inputs.append((args, kwargs))
            return rv

        return wrap

    def dump_output(func):
        def wrap(*args, **kwargs):
            rv = func(*args, **kwargs)
            outputs.append(rv)
            return rv

        return wrap

    hello.decorated_by(dump_input)
    hello.decorated_by(dump_output)
    assert hello("world") == "hello world"
    assert inputs == [(("world",), {})]
    assert outputs == ["hello world"]


def test_hook_method_with_decorator():
    class Person:
        @hook
        def hello(self, name):
            return f"hello {name}"

    results = []

    def dump_invocation(func):
        def wrap(*args, **kwargs):
            rv = func(*args, **kwargs)
            results.append((args, kwargs, rv))
            return rv

        return wrap

    Person.hello.decorated_by(dump_invocation)

    jack = Person()
    assert jack.hello("world") == "hello world"
    assert results == [
        (
            (
                jack,
                "world",
            ),
            {},
            "hello world",
        )
    ]
