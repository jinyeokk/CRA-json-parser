# Phase 5 — 파일 입출력 설계

## 목표
Phase 1~4에서 구현한 Tokenizer / Parser / Serializer를 조합하여
표준 라이브러리 `json` 모듈과 동일한 인터페이스(`load`, `loads`, `dump`, `dumps`)를 제공한다.

---

## 인터페이스 정의

```python
# 파싱
def loads(s: str) -> object: ...
def load(fp) -> object: ...

# 직렬화
def dumps(obj: object, indent: int | None = None) -> str: ...
def dump(obj: object, fp, indent: int | None = None) -> None: ...
```

| 함수     | 입력             | 출력           | 내부 호출 |
|---------|-----------------|----------------|---------|
| `loads` | JSON 문자열      | Python 객체    | `tokenize` → `parse` |
| `load`  | 파일 객체 (읽기) | Python 객체    | `fp.read()` → `loads` |
| `dumps` | Python 객체      | JSON 문자열    | `_serialize` |
| `dump`  | Python 객체 + 파일 객체 (쓰기) | `None` | `dumps` → `fp.write` |

---

## 구현 내용

### `loads`

```python
def loads(s: str) -> object:
    tokens = tokenize(s)
    return parse(tokens)
```

### `load`

```python
def load(fp) -> object:
    return loads(fp.read())
```

- `fp`: `read()` 메서드를 가진 객체 (파일, `StringIO` 등)
- 인코딩은 호출자가 `open(..., encoding='utf-8')` 으로 제어한다 (라이브러리 내부에서 강제하지 않음)

### `dumps`

```python
def dumps(obj: object, indent: int | None = None) -> str:
    return _serialize(obj, indent=indent, level=0)
```

### `dump`

```python
def dump(obj: object, fp, indent: int | None = None) -> None:
    fp.write(dumps(obj, indent=indent))
```

---

## 파일 처리 책임 분리

라이브러리는 파일 열기 / 닫기를 담당하지 않는다.
호출자가 `open()`으로 파일을 열고 컨텍스트 매니저로 관리한다.

```python
# 읽기
with open("data.json", encoding="utf-8") as f:
    obj = load(f)

# 쓰기
with open("output.json", "w", encoding="utf-8") as f:
    dump(obj, f, indent=2)
```

이 설계는 표준 라이브러리 `json` 모듈과 동일하다.

---

## `__init__.py` 공개 API

```python
# jsonparser/__init__.py
from .io import load, loads, dump, dumps

__all__ = ["load", "loads", "dump", "dumps"]
```

---

## 스모크 테스트 (main.py 확인용)

```python
import jsonparser

# loads / dumps 왕복
src = '{"name": "Alice", "scores": [10, 20], "active": true}'
obj = jsonparser.loads(src)
print(obj)          # {'name': 'Alice', 'scores': [10, 20], 'active': True}
print(jsonparser.dumps(obj))
# {"name":"Alice","scores":[10,20],"active":true}

# 파일 쓰기
with open("output.json", "w", encoding="utf-8") as f:
    jsonparser.dump(obj, f, indent=2)

# 파일 읽기
with open("output.json", encoding="utf-8") as f:
    loaded = jsonparser.load(f)

assert loaded == obj
print("파일 입출력 테스트 통과")
```

---

## 완료 기준

- [ ] `loads(s)` 구현
- [ ] `load(fp)` 구현
- [ ] `dumps(obj, indent=None)` 구현 (Phase 4 위임)
- [ ] `dump(obj, fp, indent=None)` 구현
- [ ] `jsonparser/__init__.py` 에서 4개 함수 공개 export
- [ ] `loads` → `dumps` → `loads` 왕복 일치 확인
- [ ] 실제 파일 쓰기 / 읽기 스모크 테스트 통과
