import os

from abacusevents.utils import env, lowercase_first


def test_env_is_short_for_os_dot_environ():
    os.environ['FOO'] = 'BAR'
    assert env('FOO') == 'BAR'


def test_env_lets_you_specify_a_default_value():
    default = env('NOT_THERE', 'FOO')
    assert default == 'FOO'


def test_env_wont_explode():
    assert env('NOTHING') is None


def test_lowercase_first():
    assert lowercase_first('Ping') == 'ping'
    assert lowercase_first('') == ''
    assert lowercase_first('fOO') == 'fOO'
    assert lowercase_first(None) == ''
    assert lowercase_first(False) == ''
    assert lowercase_first([]) == ''
    assert lowercase_first([1]) == ''
    assert lowercase_first((1,)) == ''
