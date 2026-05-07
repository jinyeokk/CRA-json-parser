# Phase 2 — Parser 설계

## 목표
Phase 1 Tokenizer가 생성한 `Token` 리스트를 소비하여 JSON 값을 재귀적으로 파싱하고,
Python 네이티브 객체(`dict`, `list`, `str`, `int`, `float`, `bool`, `None`)로 반환한다.

> Phase 2와 Phase 3(타입 변환)을 통합 구현한다.
> 파서가 직접 Python 타입을 반환하므로 별도 AST 노드 없이 단순하게 유지한다.

---

## 인터페이스

```python
def parse(tokens: list[Token]) -> object:
    ...
```

- 입력: `tokenize()`가 반환한 `Token` 리스트
- 출력: JSON 최상위 값에 해당하는 Python 객체
- 예외: 문법 오류 → `JSONDecodeError` (Phase 6 전까지는 `ValueError` 임시 대체)

편의 함수:

```python
def parse_string(text: str) -> object:
    return parse(tokenize(text))
```

---

## 파서 구조 — 재귀 하강 파서 (Recursive Descent)

토큰 스트림을 순서대로 소비하는 커서(cursor) 기반으로 구현한다.

```python
class Parser:
    def __init__(self, tokens: list[Token]):
        self.tokens = tokens
        self.pos = 0          # 현재 커서 위치

    def peek(self) -> Token:  # 현재 토큰 확인 (소비 안 함)
    def consume(self) -> Token:  # 현재 토큰 반환 후 pos += 1
    def expect(self, type: TokenType) -> Token:  # 타입 불일치 시 오류
    def parse_value(self) -> object:  # 진입점
```

---

## 파싱 규칙

### `parse_value` — 분기점

```
현재 토큰 타입에 따라:
  LBRACE   → parse_object()
  LBRACKET → parse_array()
  STRING   → 토큰의 value(str) 반환
  NUMBER   → 토큰의 value(int|float) 반환
  TRUE     → True 반환
  FALSE    → False 반환
  NULL     → None 반환
  그 외    → 오류
```

### `parse_object` — `{}`

```
'{' 소비
result = {}

현재 토큰이 '}' 이면 → {} 반환  (빈 객체)

루프:
  key   = expect(STRING).value
  ':'   = expect(COLON)
  value = parse_value()
  result[key] = value

  다음 토큰이 ',' 이면 소비 후 계속
  다음 토큰이 '}' 이면 소비 후 종료
  그 외 → 오류

return result
```

### `parse_array` — `[]`

```
'[' 소비
result = []

현재 토큰이 ']' 이면 → [] 반환  (빈 배열)

루프:
  value = parse_value()
  result.append(value)

  다음 토큰이 ',' 이면 소비 후 계속
  다음 토큰이 ']' 이면 소비 후 종료
  그 외 → 오류

return result
```

---

## 타입 변환 (Phase 3 통합)

Tokenizer에서 이미 변환된 값을 그대로 사용한다.

| Token.type | Token.value 타입 | Parser 반환값 |
|------------|-----------------|--------------|
| `STRING`   | `str`           | `str`        |
| `NUMBER`   | `int` / `float` | `int` / `float` |
| `TRUE`     | `str` `"true"`  | `True`       |
| `FALSE`    | `str` `"false"` | `False`      |
| `NULL`     | `str` `"null"`  | `None`       |

- `TRUE` / `FALSE` / `NULL`의 Python 변환은 `parse_value` 내부에서 처리한다.
- Tokenizer는 값을 문자열 그대로 유지하고, Parser가 최종 변환을 담당한다.

---

## 처리 흐름 예시

입력: `{"a": [1, false]}`

```
tokenize → [LBRACE, STRING("a"), COLON, LBRACKET,
             NUMBER(1), COMMA, FALSE, RBRACKET, RBRACE, EOF]

parse_value
  └─ parse_object
       ├─ consume LBRACE
       ├─ key = "a"
       ├─ consume COLON
       ├─ parse_value
       │    └─ parse_array
       │         ├─ consume LBRACKET
       │         ├─ parse_value → 1
       │         ├─ consume COMMA
       │         ├─ parse_value → False
       │         └─ consume RBRACKET → [1, False]
       └─ consume RBRACE → {"a": [1, False]}
```

---

## 오류 케이스

| 상황 | 예시 입력 | 오류 메시지 |
|------|----------|------------|
| 키가 문자열이 아님 | `{1: "v"}` | `Expected STRING, got NUMBER` |
| `:` 누락 | `{"k" "v"}` | `Expected COLON, got STRING` |
| 구분자 오류 | `[1 2]` | `Expected COMMA or RBRACKET` |
| 값 위치에 잘못된 토큰 | `{"k": }` | `Unexpected token RBRACE` |
| EOF 조기 도달 | `{"k":` | `Unexpected EOF` |

---

## 스모크 테스트 (main.py 확인용)

```python
from jsonparser.parser import parse_string

result = parse_string('{"name": "Alice", "scores": [10, 20.5], "active": true, "extra": null}')
print(result)
# {"name": "Alice", "scores": [10, 20.5], "active": True, "extra": None}

print(parse_string('[]'))   # []
print(parse_string('42'))   # 42
print(parse_string('"hi"')) # hi
```

---

## 완료 기준

- [ ] `Parser` 클래스 구현 (`peek`, `consume`, `expect`)
- [ ] `parse_value` 분기 처리
- [ ] `parse_object` 구현 (빈 객체 포함)
- [ ] `parse_array` 구현 (빈 배열 포함)
- [ ] Python 타입 변환 (bool, None 포함)
- [ ] 중첩 구조 처리 (object 안 array, array 안 object 등)
- [ ] 스모크 테스트 통과
- [ ] `tests/test_parser.py` 작성 및 전체 통과
