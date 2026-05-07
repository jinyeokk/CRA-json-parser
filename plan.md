# JSON Parser Library — PoC 구현 계획

단계별로 하나씩 구현하는 PoC. 외부 라이브러리(`json` 모듈 등) 없이 직접 파서를 작성하는 것을 목표로 한다.

---

## 단계 개요

| 단계 | 내용 | 테스트 파일 | 상태 |
|------|------|------------|------|
| 1 | Tokenizer (어휘 분석기) | `tests/test_tokenizer.py` | 완료 |
| 2 | Parser (구문 분석기) | `tests/test_parser.py` | 완료 |
| 3 | Python 객체로 변환 | `tests/test_parser.py` (공유) | 완료 |
| 4 | JSON 직렬화 (Python → JSON 문자열) | `tests/test_serializer.py` | 완료 |
| 5 | 파일 입출력 (load / dump) | `tests/test_io.py` | 완료 |
| 6 | 오류 처리 및 예외 정의 | `tests/test_errors.py` | 완료 |
| 7 | 통합 테스트 | `tests/test_integration.py` | 완료 |

> 각 Phase 구현 완료 시 해당 테스트 파일도 함께 작성·통과 후 커밋한다.

---

## 단계별 상세

### 1단계 — Tokenizer
JSON 문자열을 읽어 의미 있는 토큰으로 쪼갠다.

- 처리할 토큰 종류
  - `{` `}` `[` `]` `:` `,`
  - 문자열 (`"..."`)
  - 숫자 (정수 / 부동소수점)
  - 리터럴 (`true`, `false`, `null`)
- 공백·개행·탭은 건너뜀
- 결과: `Token(type, value)` 리스트

### 2단계 — Parser
토큰 리스트를 받아 JSON 구조를 재귀적으로 파싱한다.

- 파싱 대상
  - Object (`{}`)
  - Array (`[]`)
  - String, Number, Boolean, Null
- 재귀 하강 파서(recursive descent parser) 방식으로 구현

### 3단계 — Python 객체 변환
파서 결과를 Python 네이티브 타입으로 매핑한다.

| JSON 타입 | Python 타입 |
|-----------|------------|
| object    | `dict`     |
| array     | `list`     |
| string    | `str`      |
| number    | `int` / `float` |
| true/false | `bool`    |
| null      | `None`     |

### 4단계 — 직렬화 (Serializer)
Python 객체를 JSON 문자열로 변환한다.

- `dumps(obj, indent=None)` 구현
- `indent` 옵션 지원 (pretty-print)
- 지원 타입: `dict`, `list`, `str`, `int`, `float`, `bool`, `None`

### 5단계 — 파일 입출력
파일에서 읽고 파일로 쓰는 인터페이스를 제공한다.

- `load(fp)` — 파일 객체에서 읽어 파싱
- `loads(s)` — 문자열에서 파싱
- `dump(obj, fp, indent=None)` — 파일 객체로 직렬화해 저장
- `dumps(obj, indent=None)` — 문자열로 직렬화

### 6단계 — 오류 처리
파싱 실패 시 명확한 오류를 던진다.

- `JSONDecodeError(message, pos)` 예외 클래스 정의
- 오류 위치(line, column) 포함
- 처리할 케이스
  - 예상치 못한 토큰
  - 닫히지 않은 문자열 / 괄호
  - 잘못된 이스케이프 시퀀스
  - 숫자 형식 오류

### 7단계 — 테스트
각 단계별 동작을 검증하는 테스트를 작성한다.

- **프레임워크: 표준 라이브러리 `unittest` 만 사용. 외부 패키지 금지.**
- 단위 테스트: Tokenizer, Parser, Serializer 각각 (`unittest.TestCase` 서브클래스)
- 통합 테스트: `loads` → `dumps` 왕복 일치 확인
- 엣지 케이스: 빈 객체/배열, 중첩 구조, 유니코드, 특수문자 이스케이프
- 파일 I/O 테스트: `tempfile` 모듈로 임시 파일 사용

---

## 파일 구조 (예정)

```
jsonparser/
├── main.py              # 사용 예시 및 진입점
├── plan.md              # 이 파일
└── jsonparser/
    ├── __init__.py      # load, loads, dump, dumps 노출
    ├── tokenizer.py     # 1단계
    ├── parser.py        # 2~3단계
    ├── serializer.py    # 4단계
    ├── io.py            # 5단계
    └── exceptions.py    # 6단계
```

---

## 구현 순서 원칙

- 각 단계 완료 후 간단한 스모크 테스트를 `main.py`에서 실행해 확인
- 다음 단계로 넘어가기 전에 현재 단계가 정상 동작하는지 검증
- 리팩터링은 7단계 이후에 고려
