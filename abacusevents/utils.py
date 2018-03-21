import os


def env(variable: str, default=None):
    return os.environ.get(variable, default)


def lowercase_first(string: str) -> str:
    return string[:1].lower() + string[1:] if type(string) == str else ''
