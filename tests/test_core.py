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
