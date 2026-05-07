from dataclasses import dataclass
from enum import Enum, auto


class TokenType(Enum):
    LBRACE   = auto()
    RBRACE   = auto()
    LBRACKET = auto()
    RBRACKET = auto()
    COLON    = auto()
    COMMA    = auto()
    STRING   = auto()
    NUMBER   = auto()
    TRUE     = auto()
    FALSE    = auto()
    NULL     = auto()
    EOF      = auto()


@dataclass
class Token:
    type:  TokenType
    value: object
    pos:   int


_ESCAPES = {
    '"':  '"',
    '\\': '\\',
    '/':  '/',
    'b':  '\b',
    'f':  '\f',
    'n':  '\n',
    'r':  '\r',
    't':  '\t',
}

_STRUCTURAL = {
    '{': TokenType.LBRACE,
    '}': TokenType.RBRACE,
    '[': TokenType.LBRACKET,
    ']': TokenType.RBRACKET,
    ':': TokenType.COLON,
    ',': TokenType.COMMA,
}


def tokenize(text: str) -> list:
    tokens = []
    pos = 0
    length = len(text)

    while pos < length:
        ch = text[pos]

        if ch in ' \t\n\r':
            pos += 1
            continue

        if ch in _STRUCTURAL:
            tokens.append(Token(_STRUCTURAL[ch], ch, pos))
            pos += 1
            continue

        if ch == '"':
            token, pos = _scan_string(text, pos)
            tokens.append(token)
            continue

        if ch == '-' or ch.isdigit():
            token, pos = _scan_number(text, pos)
            tokens.append(token)
            continue

        if ch == 't':
            _expect_literal(text, pos, 'true')
            tokens.append(Token(TokenType.TRUE, 'true', pos))
            pos += 4
            continue

        if ch == 'f':
            _expect_literal(text, pos, 'false')
            tokens.append(Token(TokenType.FALSE, 'false', pos))
            pos += 5
            continue

        if ch == 'n':
            _expect_literal(text, pos, 'null')
            tokens.append(Token(TokenType.NULL, 'null', pos))
            pos += 4
            continue

        raise ValueError(f"Unexpected character: {ch!r} at position {pos}")

    tokens.append(Token(TokenType.EOF, None, pos))
    return tokens


def _scan_string(text: str, start: int) -> tuple:
    pos = start + 1  # 여는 " 건너뜀
    length = len(text)
    chars = []

    while pos < length:
        ch = text[pos]

        if ch == '"':
            return Token(TokenType.STRING, ''.join(chars), start), pos + 1

        if ch == '\\':
            pos += 1
            if pos >= length:
                raise ValueError(f"Unterminated string starting at position {start}")
            esc = text[pos]
            if esc in _ESCAPES:
                chars.append(_ESCAPES[esc])
            elif esc == 'u':
                if pos + 4 >= length:
                    raise ValueError(f"Invalid \\uXXXX escape at position {pos - 1}")
                hex_str = text[pos + 1:pos + 5]
                if not all(c in '0123456789abcdefABCDEF' for c in hex_str):
                    raise ValueError(f"Invalid \\uXXXX escape at position {pos - 1}")
                chars.append(chr(int(hex_str, 16)))
                pos += 4
            else:
                raise ValueError(f"Invalid escape sequence: \\{esc} at position {pos - 1}")
            pos += 1
            continue

        chars.append(ch)
        pos += 1

    raise ValueError(f"Unterminated string starting at position {start}")


def _scan_number(text: str, start: int) -> tuple:
    pos = start
    length = len(text)
    is_float = False

    if text[pos] == '-':
        pos += 1

    if pos >= length or not text[pos].isdigit():
        raise ValueError(f"Invalid number literal at position {start}")

    if text[pos] == '0':
        pos += 1
    else:
        while pos < length and text[pos].isdigit():
            pos += 1

    if pos < length and text[pos] == '.':
        is_float = True
        pos += 1
        if pos >= length or not text[pos].isdigit():
            raise ValueError(f"Invalid number literal at position {start}")
        while pos < length and text[pos].isdigit():
            pos += 1

    if pos < length and text[pos] in 'eE':
        is_float = True
        pos += 1
        if pos < length and text[pos] in '+-':
            pos += 1
        if pos >= length or not text[pos].isdigit():
            raise ValueError(f"Invalid number literal at position {start}")
        while pos < length and text[pos].isdigit():
            pos += 1

    raw = text[start:pos]
    value = float(raw) if is_float else int(raw)
    return Token(TokenType.NUMBER, value, start), pos


def _expect_literal(text: str, pos: int, literal: str) -> None:
    end = pos + len(literal)
    if text[pos:end] != literal:
        raise ValueError(f"Invalid literal: {text[pos:end]!r} at position {pos}")
