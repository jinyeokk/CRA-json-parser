# Phase 6 — 오류 처리 설계

## 목표
Phase 1~5에서 임시로 `ValueError`를 던지던 부분을 전용 예외 클래스로 교체하고,
오류 위치(line, column)와 명확한 메시지를 함께 제공한다.

---

## 예외 클래스

```python
class JSONDecodeError(ValueError):
    """JSON 파싱 실패 예외.

    Attributes:
        msg:    오류 설명 문자열
        doc:    파싱 중이던 원본 문자열
        pos:    오류 발생 위치 (문자 인덱스)
        lineno: 오류 발생 줄 번호 (1-based)
        colno:  오류 발생 열 번호 (1-based)
    """

    def __init__(self, msg: str, doc: str, pos: int):
        lineno, colno = _calc_position(doc, pos)
        self.msg    = msg
        self.doc    = doc
        self.pos    = pos
        self.lineno = lineno
        self.colno  = colno
        errmsg = f"{msg}: line {lineno} column {colno} (char {pos})"
        super().__init__(errmsg)


def _calc_position(doc: str, pos: int) -> tuple[int, int]:
    """pos 이전까지 개행 수를 세어 (line, col) 반환."""
    prefix = doc[:pos]
    lineno = prefix.count('\n') + 1
    colno  = pos - prefix.rfind('\n')  # rfind 반환 -1이면 pos+1
    return lineno, colno
```

`ValueError`를 상속하므로 기존 `except ValueError`도 호환된다.

---

## 오류 발생 지점 및 메시지

### Tokenizer 오류

| 상황 | 메시지 예시 |
|------|-----------|
| 닫히지 않은 문자열 | `Unterminated string starting at` |
| 잘못된 이스케이프 (`\q`) | `Invalid escape sequence: \q` |
| `\uXXXX` 형식 오류 | `Invalid \\uXXXX escape` |
| 인식 불가 문자 | `Unexpected character: '@'` |
| 잘못된 숫자 형식 | `Invalid number literal` |
| `true/false/null` 오타 | `Invalid literal: 'tru'` |

### Parser 오류

| 상황 | 메시지 예시 |
|------|-----------|
| 키가 문자열 아님 | `Object key must be a string, got NUMBER` |
| `:` 누락 | `Expected ':' after object key` |
| `,` 또는 닫는 괄호 누락 | `Expected ',' or '}' in object` |
| 예상치 못한 토큰 | `Unexpected token: RBRACE` |
| 조기 EOF | `Unexpected end of input` |
| 최상위 값 뒤 잉여 토큰 | `Extra data after end of JSON` |

---

## 오류 전파 구조

```
tokenize(text)
  └─ Tokenizer 내부에서 발견 시
       └─ raise JSONDecodeError(msg, text, pos)

parse(tokens, original_text)
  └─ Parser 내부에서 발견 시
       └─ raise JSONDecodeError(msg, original_text, token.pos)
```

`parse`는 `original_text`를 추가 인자로 받아야 한다 (오류 위치 계산용).

---

## Phase 1~5 코드 수정 범위

| 파일 | 변경 내용 |
|------|---------|
| `tokenizer.py` | `ValueError` → `JSONDecodeError` 교체, `text` / `pos` 전달 |
| `parser.py` | `ValueError` → `JSONDecodeError` 교체, `original_text` 인자 추가 |
| `serializer.py` | `TypeError` 유지 (파싱 오류 아님), `ValueError` for inf/nan 유지 |
| `io.py` | 변경 없음 (예외는 하위 모듈에서 전파) |
| `exceptions.py` | `JSONDecodeError`, `_calc_position` 신규 정의 |

---

## 오류 메시지 출력 예시

```
JSONDecodeError: Unexpected character: '@': line 2 column 5 (char 14)
```

```
JSONDecodeError: Unterminated string starting at: line 1 column 1 (char 0)
```

---

## 스모크 테스트 (main.py 확인용)

```python
import jsonparser
from jsonparser.exceptions import JSONDecodeError

bad_inputs = [
    ('{"key": @}',      "Unexpected character"),
    ('{"key": "val}',   "Unterminated string"),
    ('{1: "val"}',      "Object key must be a string"),
    ('{"k": }',         "Unexpected token"),
    ('{"k": 1} extra',  "Extra data"),
]

for src, expected_msg in bad_inputs:
    try:
        jsonparser.loads(src)
        print(f"FAIL: 오류가 발생해야 함 → {src!r}")
    except JSONDecodeError as e:
        print(f"OK  ({expected_msg}): {e}")
```

---

## 완료 기준

- [ ] `exceptions.py` — `JSONDecodeError` 클래스 정의
- [ ] `_calc_position` — line / column 계산 함수
- [ ] Tokenizer의 모든 `ValueError` → `JSONDecodeError` 교체
- [ ] Parser의 모든 `ValueError` → `JSONDecodeError` 교체
- [ ] 오류 메시지에 line / column / char 위치 포함
- [ ] `JSONDecodeError`가 `ValueError` 서브클래스임을 검증
- [ ] 스모크 테스트 통과
