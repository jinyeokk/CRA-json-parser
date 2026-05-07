import math

_ESCAPE_MAP = {
    '"':  '\\"',
    '\\': '\\\\',
    '\b': '\\b',
    '\f': '\\f',
    '\n': '\\n',
    '\r': '\\r',
    '\t': '\\t',
}


def dumps(obj: object, indent=None) -> str:
    return _serialize(obj, indent, 0)


def _serialize(obj, indent, level: int) -> str:
    if isinstance(obj, bool):
        return 'true' if obj else 'false'
    if isinstance(obj, int):
        return str(obj)
    if isinstance(obj, float):
        return _serialize_float(obj)
    if isinstance(obj, str):
        return _escape_string(obj)
    if obj is None:
        return 'null'
    if isinstance(obj, dict):
        return _serialize_dict(obj, indent, level)
    if isinstance(obj, list):
        return _serialize_list(obj, indent, level)
    raise TypeError(f"지원하지 않는 타입: {type(obj).__name__}")


def _serialize_float(v: float) -> str:
    if math.isnan(v) or math.isinf(v):
        raise ValueError(f"JSON은 {v}를 직렬화할 수 없음")
    return repr(v)


def _escape_string(s: str) -> str:
    chars = []
    for ch in s:
        if ch in _ESCAPE_MAP:
            chars.append(_ESCAPE_MAP[ch])
        elif ord(ch) < 0x20:
            chars.append(f'\\u{ord(ch):04x}')
        else:
            chars.append(ch)
    return '"' + ''.join(chars) + '"'


def _serialize_dict(obj: dict, indent, level: int) -> str:
    if not obj:
        return '{}'

    for key in obj:
        if not isinstance(key, str):
            raise TypeError(f"dict 키는 str이어야 합니다: {type(key).__name__}")

    if indent is None:
        items = [_escape_string(k) + ':' + _serialize(v, None, 0)
                 for k, v in obj.items()]
        return '{' + ','.join(items) + '}'

    pad      = ' ' * indent * (level + 1)
    pad_close = ' ' * indent * level
    items = [pad + _escape_string(k) + ': ' + _serialize(v, indent, level + 1)
             for k, v in obj.items()]
    return '{\n' + ',\n'.join(items) + '\n' + pad_close + '}'


def _serialize_list(obj: list, indent, level: int) -> str:
    if not obj:
        return '[]'

    if indent is None:
        items = [_serialize(v, None, 0) for v in obj]
        return '[' + ','.join(items) + ']'

    pad       = ' ' * indent * (level + 1)
    pad_close = ' ' * indent * level
    items = [pad + _serialize(v, indent, level + 1) for v in obj]
    return '[\n' + ',\n'.join(items) + '\n' + pad_close + ']'
