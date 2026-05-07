from .tokenizer import tokenize
from .parser import parse
from .serializer import dumps as _dumps


def loads(s: str) -> object:
    return parse(tokenize(s), s)


def load(fp) -> object:
    return loads(fp.read())


def dumps(obj: object, indent=None) -> str:
    return _dumps(obj, indent=indent)


def dump(obj: object, fp, indent=None) -> None:
    fp.write(dumps(obj, indent=indent))
