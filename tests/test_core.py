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


def test_hook_func_with_alias():
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    hello_alias = hello

    with hook(hello) as hooker:
        inputs = []

        def dump_input(*args, **kwargs):
            inputs.append((args, kwargs))

        with hooker.call_before(dump_input):
            assert hello_alias(*args, **kwargs) == rv
            assert inputs == [(args, kwargs)]


def test_hook_func_with_alias_outside():
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    hello_alias = hello

    def inner_call():
        with hook(hello) as hooker:
            inputs = []

            def dump_input(*args, **kwargs):
                inputs.append((args, kwargs))

            with hooker.call_before(dump_input):
                assert hello_alias(*args, **kwargs) == rv
                assert inputs == [(args, kwargs)]

    inner_call()


def test_hook_func_with_isolating_closure():
    def hello(name):
        return f"hello {name}"

    args = ("world",)
    kwargs = {}
    rv = "hello world"

    def make_closure(hello):
        # frame 2
        def inner_call():
            # frame 3
            # hello from frame 2
            assert hello(*args, **kwargs) == rv
            assert inputs == [(args, kwargs)]

        return inner_call

    # frame 1
    # pass as argument before hooking
    func = make_closure(hello)

    with hook(hello) as hooker:
        inputs = []

        def dump_input(*args, **kwargs):
            inputs.append((args, kwargs))

        with hooker.call_before(dump_input):
            func()
