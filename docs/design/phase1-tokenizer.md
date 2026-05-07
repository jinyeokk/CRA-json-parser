# Phase 1 — Tokenizer 설계

## 목표
JSON 문자열을 입력받아 의미 있는 최소 단위(토큰)의 리스트로 변환한다.
파서는 이 토큰 리스트만 보고 구조를 분석하므로, Tokenizer는 문자 수준의 처리를 완전히 책임진다.

---

## 토큰 종류

| TokenType | 해당 문자 / 패턴 | 예시 값 |
|-----------|----------------|---------|
| `LBRACE`  | `{`            | `{`     |
| `RBRACE`  | `}`            | `}`     |
| `LBRACKET`| `[`            | `[`     |
| `RBRACKET`| `]`            | `]`     |
| `COLON`   | `:`            | `:`     |
| `COMMA`   | `,`            | `,`     |
| `STRING`  | `"..."`        | `hello` (따옴표 제거) |
| `NUMBER`  | 정수 / 부동소수점 | `42`, `3.14`, `-1e10` |
| `TRUE`    | `true`         | `true`  |
| `FALSE`   | `false`        | `false` |
| `NULL`    | `null`         | `null`  |
| `EOF`     | 입력 끝        | —       |

---

## 데이터 구조

```python
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
    value: object      # str | int | float | bool | None
    pos:   int         # 원본 문자열에서의 시작 위치 (오류 추적용)
```

---

## 인터페이스

```python
def tokenize(text: str) -> list[Token]:
    ...
```

- 입력: JSON 원본 문자열
- 출력: `Token` 리스트 (마지막은 항상 `EOF`)
- 예외: 인식 불가 문자, 닫히지 않은 문자열 → `JSONDecodeError` (Phase 6에서 정의; Phase 1에서는 `ValueError`로 임시 대체)

---

## 처리 흐름

```
text
 │
 ▼
현재 위치(pos) 기준으로 문자 1개 읽기
 │
 ├─ 공백 / \t / \n / \r  →  건너뜀
 │
 ├─ { } [ ] : ,          →  해당 TokenType 발행
 │
 ├─ "                    →  문자열 스캔
 │    └─ 닫는 " 까지 읽기 (이스케이프 처리 포함)
 │
 ├─ - 또는 0-9           →  숫자 스캔
 │    └─ 정수 / 소수점 / 지수 처리
 │
 ├─ t                    →  'true' 확인
 ├─ f                    →  'false' 확인
 ├─ n                    →  'null' 확인
 │
 └─ 그 외                →  오류
```

---

## 문자열 스캔 상세

- `"` 를 만나면 닫는 `"` 까지 문자를 누적
- 이스케이프 시퀀스 처리

| 이스케이프 | 변환 결과 |
|-----------|----------|
| `\"`      | `"`      |
| `\\`      | `\`      |
| `\/`      | `/`      |
| `\b`      | 백스페이스 |
| `\f`      | 폼피드   |
| `\n`      | 개행     |
| `\r`      | 캐리지 리턴 |
| `\t`      | 탭       |
| `\uXXXX`  | 유니코드 문자 |

- 닫는 `"` 없이 문자열 끝 도달 시 오류

---

## 숫자 스캔 상세

JSON number 문법:
```
number  = [ '-' ] int [ frac ] [ exp ]
int     = '0' | [1-9] digit*
frac    = '.' digit+
exp     = ('e' | 'E') ['+' | '-'] digit+
```

- `.` 또는 `e/E` 가 포함되면 `float`, 그렇지 않으면 `int`로 변환

---

## 스모크 테스트 (main.py 확인용)

```python
from jsonparser.tokenizer import tokenize

tokens = tokenize('{"key": [1, true, null]}')
for t in tokens:
    print(t)
```

예상 출력:
```
Token(LBRACE,   '{',   0)
Token(STRING,   'key', 1)
Token(COLON,    ':',   6)
Token(LBRACKET, '[',   8)
Token(NUMBER,   1,     9)
Token(COMMA,    ',',   10)
Token(TRUE,     'true',12)
Token(COMMA,    ',',   16)
Token(NULL,     'null',18)
Token(RBRACKET, ']',   22)
Token(RBRACE,   '}',   23)
Token(EOF,      None,  24)
```

---

## 완료 기준

- [ ] `TokenType`, `Token` 정의 완료
- [ ] `tokenize()` 구현 완료
- [ ] 6가지 구조 문자 처리
- [ ] 문자열 (이스케이프 포함) 처리
- [ ] 숫자 (정수 / 부동소수점 / 지수) 처리
- [ ] `true` / `false` / `null` 처리
- [ ] 공백 무시
- [ ] 스모크 테스트 통과
- [ ] `tests/test_tokenizer.py` 작성 및 전체 통과
