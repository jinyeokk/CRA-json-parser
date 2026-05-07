# Phase 3 — Python 타입 변환 설계

## 목표
Parser가 반환한 중간 표현을 Python 표준 타입으로 확정한다.
Phase 2와 통합 구현되므로, 이 문서는 타입 변환 규칙과 엣지 케이스를 명확히 정의하는 데 집중한다.

---

## 타입 매핑 규칙

| JSON 명세 타입 | 예시 리터럴 | Python 타입 | 변환 방식 |
|--------------|------------|------------|---------|
| object       | `{"k": 1}` | `dict`     | 키-값 재귀 수집 |
| array        | `[1, 2]`   | `list`     | 요소 재귀 수집  |
| string       | `"hello"`  | `str`      | 이스케이프 해제 후 그대로 |
| number (정수) | `42`, `-7` | `int`      | `int()` 변환 |
| number (실수) | `3.14`, `1e5` | `float` | `float()` 변환 |
| true         | `true`     | `bool` (`True`)  | 리터럴 매핑 |
| false        | `false`    | `bool` (`False`) | 리터럴 매핑 |
| null         | `null`     | `None`     | 리터럴 매핑 |

---

## 숫자 판별 기준

Tokenizer 단계에서 문자열을 스캔할 때 결정한다.

```
'.' 포함  →  float
'e' 또는 'E' 포함  →  float
그 외  →  int
```

예:
- `0` → `int(0)`
- `-1` → `int(-1)`
- `1.0` → `float(1.0)`
- `1e3` → `float(1000.0)`
- `1E-2` → `float(0.01)`
- `1.5e2` → `float(150.0)`

---

## 문자열 이스케이프 해제

Tokenizer가 원본 JSON 문자열의 이스케이프 시퀀스를 Python `str`로 변환한다.
Parser는 이미 변환된 값을 받는다.

| JSON 이스케이프 | Python 문자 | 코드포인트 |
|---------------|------------|-----------|
| `\"`          | `"`        | U+0022    |
| `\\`          | `\`        | U+005C    |
| `\/`          | `/`        | U+002F    |
| `\b`          | 백스페이스  | U+0008    |
| `\f`          | 폼피드     | U+000C    |
| `\n`          | 개행       | U+000A    |
| `\r`          | CR         | U+000D    |
| `\t`          | 탭         | U+0009    |
| `\uXXXX`      | 유니코드    | 해당 코드포인트 |

`\uXXXX` 처리:
```python
char = chr(int(hex_str, 16))
```

---

## dict 키 타입 보장

JSON 명세에서 object의 키는 반드시 문자열이다.
Parser는 키 토큰이 `STRING`이 아닌 경우 오류를 발생시킨다.
결과 `dict`의 키는 항상 `str` 타입이다.

---

## 중첩 구조 처리

재귀 호출로 자동 처리된다. 별도 깊이 제한은 Phase 6(오류 처리)에서 고려한다.

```json
{
  "a": {
    "b": [1, {"c": null}]
  }
}
```

```python
{"a": {"b": [1, {"c": None}]}}
```

---

## 스모크 테스트 (main.py 확인용)

```python
from jsonparser.parser import parse_string

cases = [
    ('42',          int,   42),
    ('-3',          int,   -3),
    ('3.14',        float, 3.14),
    ('1e2',         float, 100.0),
    ('"hello"',     str,   'hello'),
    ('true',        bool,  True),
    ('false',       bool,  False),
    ('null',        type(None), None),
    ('{}',          dict,  {}),
    ('[]',          list,  []),
]

for src, expected_type, expected_val in cases:
    result = parse_string(src)
    assert isinstance(result, expected_type), f"{src}: 타입 불일치"
    assert result == expected_val,            f"{src}: 값 불일치"

print("모든 타입 변환 테스트 통과")
```

---

## 완료 기준

- [ ] 정수 / 부동소수점 구분 변환
- [ ] `true` → `True`, `false` → `False`, `null` → `None` 변환
- [ ] 문자열 이스케이프 시퀀스 8종 처리
- [ ] `\uXXXX` 유니코드 이스케이프 처리
- [ ] `dict` 키가 항상 `str`임을 보장
- [ ] 중첩 구조 재귀 변환 정상 동작
- [ ] 스모크 테스트 통과
