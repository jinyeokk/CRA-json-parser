# Phase 7 — 테스트 설계

## 목표
Phase 1~6 구현 전체를 체계적으로 검증한다.
단위 테스트로 각 모듈을 독립 검증하고, 통합 테스트로 전체 파이프라인을 확인한다.
**테스트 프레임워크: Python 표준 라이브러리 `unittest` 만 사용한다. 외부 패키지 금지.**

---

## 테스트 파일 구조

```
tests/
├── __init__.py
├── test_tokenizer.py     # Phase 1
├── test_parser.py        # Phase 2~3
├── test_serializer.py    # Phase 4
├── test_io.py            # Phase 5
├── test_errors.py        # Phase 6
└── test_integration.py   # 통합
```

---

## Phase 1 — Tokenizer 테스트 (`test_tokenizer.py`)

```python
import unittest
from jsonparser.tokenizer import tokenize, TokenType
from jsonparser.exceptions import JSONDecodeError


class TestSingleTokens(unittest.TestCase):

    def test_structural_chars(self):
        pairs = [
            ('{', TokenType.LBRACE),
            ('}', TokenType.RBRACE),
            ('[', TokenType.LBRACKET),
            (']', TokenType.RBRACKET),
            (':', TokenType.COLON),
            (',', TokenType.COMMA),
        ]
        for src, expected in pairs:
            with self.subTest(src=src):
                self.assertEqual(tokenize(src)[0].type, expected)

    def test_string_token(self):
        t = tokenize('"hello"')[0]
        self.assertEqual(t.type, TokenType.STRING)
        self.assertEqual(t.value, 'hello')

    def test_integer_token(self):
        t = tokenize('42')[0]
        self.assertEqual(t.value, 42)
        self.assertIsInstance(t.value, int)

    def test_float_token(self):
        t = tokenize('3.14')[0]
        self.assertAlmostEqual(t.value, 3.14)
        self.assertIsInstance(t.value, float)

    def test_literals(self):
        self.assertEqual(tokenize('true')[0].type,  TokenType.TRUE)
        self.assertEqual(tokenize('false')[0].type, TokenType.FALSE)
        self.assertEqual(tokenize('null')[0].type,  TokenType.NULL)

    def test_whitespace_ignored(self):
        tokens = tokenize('  {  }  ')
        types = [t.type for t in tokens]
        self.assertEqual(types, [TokenType.LBRACE, TokenType.RBRACE, TokenType.EOF])

    def test_escape_sequences(self):
        t = tokenize(r'"hello\nworld"')[0]
        self.assertEqual(t.value, 'hello\nworld')

    def test_unicode_escape(self):
        t = tokenize(r'"A"')[0]  # 'A'
        self.assertEqual(t.value, 'A')


class TestTokenizerErrors(unittest.TestCase):

    def test_unterminated_string(self):
        with self.assertRaises(JSONDecodeError) as ctx:
            tokenize('"no end')
        self.assertIn('Unterminated', str(ctx.exception))

    def test_invalid_escape(self):
        with self.assertRaises(JSONDecodeError) as ctx:
            tokenize(r'"\q"')
        self.assertIn('escape', str(ctx.exception))

    def test_unexpected_character(self):
        with self.assertRaises(JSONDecodeError) as ctx:
            tokenize('@')
        self.assertIn('Unexpected character', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
```

---

## Phase 2~3 — Parser / 타입 변환 테스트 (`test_parser.py`)

```python
import unittest
from jsonparser.parser import parse_string
from jsonparser.exceptions import JSONDecodeError


class TestParserNormal(unittest.TestCase):

    def test_empty_object(self):
        self.assertEqual(parse_string('{}'), {})

    def test_empty_array(self):
        self.assertEqual(parse_string('[]'), [])

    def test_nested(self):
        result = parse_string('{"a": [1, {"b": null}]}')
        self.assertEqual(result, {"a": [1, {"b": None}]})

    def test_integer(self):
        self.assertEqual(parse_string('42'), 42)
        self.assertIsInstance(parse_string('42'), int)

    def test_float(self):
        self.assertAlmostEqual(parse_string('3.14'), 3.14)
        self.assertIsInstance(parse_string('3.14'), float)

    def test_string(self):
        self.assertEqual(parse_string('"hi"'), 'hi')

    def test_booleans(self):
        self.assertIs(parse_string('true'),  True)
        self.assertIs(parse_string('false'), False)

    def test_null(self):
        self.assertIsNone(parse_string('null'))

    def test_bool_is_not_int(self):
        self.assertIs(type(parse_string('true')), bool)

    def test_negative_number(self):
        self.assertEqual(parse_string('-7'), -7)

    def test_exponent(self):
        self.assertAlmostEqual(parse_string('1e3'), 1000.0)


class TestParserErrors(unittest.TestCase):

    def test_non_string_key(self):
        with self.assertRaises(JSONDecodeError):
            parse_string('{1: "v"}')

    def test_missing_colon(self):
        with self.assertRaises(JSONDecodeError):
            parse_string('{"k" "v"}')

    def test_trailing_comma(self):
        with self.assertRaises(JSONDecodeError):
            parse_string('{"k": 1,}')


if __name__ == '__main__':
    unittest.main()
```

---

## Phase 4 — Serializer 테스트 (`test_serializer.py`)

```python
import unittest
from jsonparser.serializer import dumps


class TestSerializerNormal(unittest.TestCase):

    def test_compact(self):
        self.assertEqual(dumps({"a": 1}), '{"a":1}')

    def test_pretty(self):
        self.assertEqual(dumps({"a": 1}, indent=2), '{\n  "a": 1\n}')

    def test_bool_true(self):
        self.assertEqual(dumps(True), 'true')

    def test_bool_false(self):
        self.assertEqual(dumps(False), 'false')

    def test_none(self):
        self.assertEqual(dumps(None), 'null')

    def test_bool_vs_int_in_dict(self):
        self.assertEqual(dumps({"v": True}), '{"v":true}')
        self.assertEqual(dumps({"v": 1}),    '{"v":1}')

    def test_nested_pretty(self):
        obj = {"arr": [1, 2]}
        expected = '{\n    "arr": [\n        1,\n        2\n    ]\n}'
        self.assertEqual(dumps(obj, indent=4), expected)

    def test_string_escape_newline(self):
        self.assertEqual(dumps("a\nb"), '"a\\nb"')

    def test_string_escape_quote(self):
        self.assertEqual(dumps('say "hi"'), '"say \\"hi\\""')


class TestSerializerErrors(unittest.TestCase):

    def test_inf_raises(self):
        with self.assertRaises(ValueError):
            dumps(float('inf'))

    def test_nan_raises(self):
        with self.assertRaises(ValueError):
            dumps(float('nan'))

    def test_unsupported_type(self):
        with self.assertRaises(TypeError):
            dumps(object())

    def test_non_string_dict_key(self):
        with self.assertRaises(TypeError):
            dumps({1: "v"})


if __name__ == '__main__':
    unittest.main()
```

---

## Phase 5 — 파일 입출력 테스트 (`test_io.py`)

```python
import unittest
import tempfile
import os
from jsonparser.io import load, loads, dump, dumps


class TestIO(unittest.TestCase):

    def test_loads_basic(self):
        self.assertEqual(loads('{"x": 1}'), {"x": 1})

    def test_load_from_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         encoding='utf-8', delete=False) as f:
            f.write('{"x": 1}')
            path = f.name
        try:
            with open(path, encoding='utf-8') as fp:
                self.assertEqual(load(fp), {"x": 1})
        finally:
            os.unlink(path)

    def test_dump_to_file(self):
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         encoding='utf-8', delete=False) as f:
            path = f.name
        try:
            with open(path, 'w', encoding='utf-8') as fp:
                dump({"x": 1}, fp)
            with open(path, encoding='utf-8') as fp:
                self.assertEqual(fp.read(), '{"x":1}')
        finally:
            os.unlink(path)

    def test_roundtrip(self):
        obj = {"name": "Alice", "scores": [10, 20], "active": True}
        with tempfile.NamedTemporaryFile(mode='w', suffix='.json',
                                         encoding='utf-8', delete=False) as f:
            path = f.name
        try:
            with open(path, 'w', encoding='utf-8') as fp:
                dump(obj, fp, indent=2)
            with open(path, encoding='utf-8') as fp:
                self.assertEqual(load(fp), obj)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
```

---

## Phase 6 — 오류 처리 테스트 (`test_errors.py`)

```python
import unittest
from jsonparser.io import loads
from jsonparser.exceptions import JSONDecodeError


class TestErrors(unittest.TestCase):

    def test_error_is_value_error(self):
        with self.assertRaises(ValueError):
            loads('{bad}')

    def test_error_has_position(self):
        try:
            loads('\n{"key": @}')
            self.fail("JSONDecodeError가 발생해야 함")
        except JSONDecodeError as e:
            self.assertEqual(e.lineno, 2)
            self.assertEqual(e.colno,  9)

    def test_extra_data(self):
        with self.assertRaises(JSONDecodeError) as ctx:
            loads('{}{}')
        self.assertIn('Extra data', str(ctx.exception))


if __name__ == '__main__':
    unittest.main()
```

---

## 통합 테스트 (`test_integration.py`)

```python
import unittest
from jsonparser.io import loads, dumps


COMPLEX = {
    "string":  'hello "world"\nnewline',
    "int":     -42,
    "float":   3.14,
    "bool_t":  True,
    "bool_f":  False,
    "null":    None,
    "array":   [1, "two", None, False],
    "nested":  {"a": {"b": {"c": 99}}},
    "unicode": "한글 テスト",
}


class TestRoundtrip(unittest.TestCase):

    def test_roundtrip_compact(self):
        self.assertEqual(loads(dumps(COMPLEX)), COMPLEX)

    def test_roundtrip_pretty(self):
        self.assertEqual(loads(dumps(COMPLEX, indent=2)), COMPLEX)


class TestEdgeCases(unittest.TestCase):

    def _check(self, src, expected):
        self.assertEqual(loads(src), expected)

    def test_empty_object(self):   self._check('{}',     {})
    def test_empty_array(self):    self._check('[]',     [])
    def test_empty_string(self):   self._check('""',     '')
    def test_zero(self):           self._check('0',      0)
    def test_negative_zero(self):  self._check('-0',     0)
    def test_large_exponent(self): self._check('1e100',  1e100)
    def test_chinese(self):        self._check('"中文"', '中文')


if __name__ == '__main__':
    unittest.main()
```

---

## 실행 방법

```bash
# 전체 실행
python -m unittest discover -s tests -v

# 단일 파일 실행
python -m unittest tests.test_tokenizer -v
python -m unittest tests.test_parser    -v

# 단일 클래스 실행
python -m unittest tests.test_tokenizer.TestSingleTokens -v

# 단일 메서드 실행
python -m unittest tests.test_tokenizer.TestSingleTokens.test_string_token -v
```

---

## 완료 기준

- [ ] `tests/__init__.py` 생성
- [ ] `test_tokenizer.py` 전체 통과
- [ ] `test_parser.py` 전체 통과
- [ ] `test_serializer.py` 전체 통과
- [ ] `test_io.py` 전체 통과
- [ ] `test_errors.py` 전체 통과
- [ ] `test_integration.py` 왕복 테스트 통과
- [ ] `test_integration.py` 엣지 케이스 전체 통과
