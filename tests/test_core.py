from hookers import hook


def test_hook_func_call_before():
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    with hook(hello) as hooker:
        inputs = []

        def dump_input(*args, **kwargs):
            inputs.append((args, kwargs))

        hooker.call_before(dump_input)

        assert hello(*args, **kwargs) == rv
        assert inputs == [(args, kwargs)]

    assert hello(*args, **kwargs) == rv
    assert inputs == [(args, kwargs)]


def test_temporary_hook_func_call_before():
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    with hook(hello) as hooker:
        inputs = []

        def dump_input(*args, **kwargs):
            inputs.append((args, kwargs))

        with hooker.call_before(dump_input):
            assert hello(*args, **kwargs) == rv
            assert inputs == [(args, kwargs)]

        assert hello(*args, **kwargs) == rv
        assert inputs == [(args, kwargs)]

    assert hello(*args, **kwargs) == rv
    assert inputs == [(args, kwargs)]
