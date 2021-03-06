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
