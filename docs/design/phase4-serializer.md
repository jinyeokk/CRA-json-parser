# Phase 4 — Serializer 설계

## 목표
Python 네이티브 객체를 JSON 형식의 문자열로 직렬화한다.
`dumps(obj, indent=None)` 하나의 함수로 compact / pretty-print 양쪽을 지원한다.

---

## 인터페이스

```python
def dumps(obj: object, indent: int | None = None) -> str:
    ...
```

- `indent=None` → compact 모드 (공백 없음)
- `indent=N` → pretty-print 모드 (N 스페이스 들여쓰기)

---

## 타입별 직렬화 규칙

| Python 타입 | JSON 출력 | 비고 |
|------------|----------|------|
| `dict`     | `{...}`  | 키는 반드시 `str`; 키도 문자열로 직렬화 |
| `list`     | `[...]`  | 요소 재귀 직렬화 |
| `str`      | `"..."`  | 이스케이프 적용 |
| `int`      | 숫자 그대로 | `True`/`False` 보다 먼저 체크 (`bool`은 `int` 서브클래스) |
| `float`    | 숫자 그대로 | `inf`, `nan` → 오류 (`float`은 유효한 JSON number가 아님) |
| `bool`     | `true` / `false` | **`int` 체크보다 먼저 분기** |
| `None`     | `null`   | |
| 그 외      | 오류     | `TypeError` |

> `bool`은 Python에서 `int`의 서브클래스이므로 반드시 `isinstance(obj, bool)` 체크를 `isinstance(obj, int)` 보다 먼저 수행해야 한다.

---

## 문자열 이스케이프 처리

직렬화 시 문자열 내 특수 문자를 이스케이프한다.

| 문자 | 이스케이프 |
|------|----------|
| `"`  | `\"`     |
| `\`  | `\\`     |
| 백스페이스 (U+0008) | `\b` |
| 폼피드 (U+000C)     | `\f` |
| 개행 (U+000A)       | `\n` |
| CR (U+000D)         | `\r` |
| 탭 (U+0009)         | `\t` |
| U+0000 ~ U+001F (그 외 제어문자) | `\uXXXX` |

---

## Compact 모드 출력 형식

```
{"key":"value","arr":[1,2,3],"flag":true}
```

- 구분자: `,` (뒤에 공백 없음), `:` (뒤에 공백 없음)

---

## Pretty-print 모드 출력 형식 (`indent=4`)

```json
{
    "key": "value",
    "arr": [
        1,
        2,
        3
    ],
    "flag": true
}
```

- 구분자: `,` + 개행, `: ` (콜론 뒤 공백 1개)
- 각 요소 앞에 현재 깊이 × indent 스페이스
- 닫는 `}` / `]` 는 부모 깊이 수준으로 내어쓰기

---

## 내부 구현 구조

재귀 함수에 `level` 인자를 전달하여 들여쓰기 깊이를 추적한다.

```python
def _serialize(obj, indent, level) -> str:
    if isinstance(obj, bool):   return "true" if obj else "false"
    if isinstance(obj, int):    return str(obj)
    if isinstance(obj, float):  ...
    if isinstance(obj, str):    return _escape_string(obj)
    if obj is None:             return "null"
    if isinstance(obj, dict):   return _serialize_dict(obj, indent, level)
    if isinstance(obj, list):   return _serialize_list(obj, indent, level)
    raise TypeError(f"지원하지 않는 타입: {type(obj)}")
```

---

## float 처리

- `math.isinf(obj)` 또는 `math.isnan(obj)` → `ValueError` 발생
- 일반 float: Python 기본 `repr`을 사용하되, 정수처럼 보이는 경우에도 소수점 유지

```python
import math

def _serialize_float(v: float) -> str:
    if math.isnan(v) or math.isinf(v):
        raise ValueError(f"JSON은 {v}를 직렬화할 수 없음")
    text = repr(v)
    return text
```

---

## 스모크 테스트 (main.py 확인용)

```python
from jsonparser.serializer import dumps

obj = {
    "name": "Alice",
    "scores": [10, 20.5],
    "active": True,
    "extra": None,
}

print(dumps(obj))
# {"name":"Alice","scores":[10,20.5],"active":true,"extra":null}

print(dumps(obj, indent=2))
# {
#   "name": "Alice",
#   "scores": [
#     10,
#     20.5
#   ],
#   "active": true,
#   "extra": null
# }
```

---

## 완료 기준

- [ ] `dumps(obj)` compact 모드 구현
- [ ] `dumps(obj, indent=N)` pretty-print 모드 구현
- [ ] `bool` 우선 분기 (`int` 서브클래스 충돌 방지)
- [ ] `float` `inf` / `nan` 오류 처리
- [ ] 문자열 이스케이프 (제어문자 `\uXXXX` 포함)
- [ ] 지원하지 않는 타입 `TypeError` 발생
- [ ] `dict` 키가 `str`이 아닌 경우 `TypeError` 발생
- [ ] 스모크 테스트 통과
- [ ] `tests/test_serializer.py` 작성 및 전체 통과
