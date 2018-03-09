import os

from events.utils import env, curry, singleton, lowercase_first


def test_env_is_short_for_os_dot_environ():
    os.environ['FOO'] = 'BAR'
    assert env('FOO') == 'BAR'


def test_env_lets_you_specify_a_default_value():
    default = env('NOT_THERE', 'FOO')
    assert default == 'FOO'


def test_curry_is_ok():
    add = curry(lambda a: lambda b: a + b)
    add1 = add(1)
    assert add1.__class__.__name__ == 'function'

    result = add1(1)
    assert result == 2


def test_singleton_is_ok_too():
    @singleton
    class Foo(object):
        pass
    a = Foo()
    b = Foo()
    assert id(a) == id(b)


def test_lowercase_first():
    assert lowercase_first('Ping') == 'ping'
    assert lowercase_first('') == ''
    assert lowercase_first('fOO') == 'fOO'
    assert lowercase_first(None) == ''
    assert lowercase_first(False) == ''
    assert lowercase_first([]) == ''
    assert lowercase_first([1]) == ''
    assert lowercase_first((1,)) == ''
