# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

---

## 프로젝트 개요

외부 `json` 모듈 없이 JSON 파서를 직접 구현하는 Python PoC 라이브러리.
`tokenize → parse → serialize → file I/O → error handling → test` 순서로 단계별로 구현한다.

---

## 브랜치 전략

각 Phase마다 별도 브랜치를 생성하고, 해당 Phase 완료 후 커밋한다.

| Phase | 브랜치명 |
|-------|---------|
| 1 | `phase/1-tokenizer` |
| 2 | `phase/2-parser` |
| 3 | `phase/3-type-conversion` |
| 4 | `phase/4-serializer` |
| 5 | `phase/5-file-io` |
| 6 | `phase/6-error-handling` |
| 7 | `phase/7-testing` |

- 각 단계는 사용자가 직접 확인한 후 다음 단계로 진행한다.
- 커밋 전 해당 Phase의 스모크 테스트를 반드시 통과해야 한다.

---

## 개발 환경

```bash
# 가상환경 활성화 (Windows)
.venv\Scripts\activate

# 테스트 실행 (전체)
python -m unittest discover -s tests -v

# 테스트 실행 (단일 파일)
python -m unittest tests.test_tokenizer -v

# 테스트 실행 (단일 클래스)
python -m unittest tests.test_tokenizer.TestSingleTokens -v

# 테스트 실행 (단일 메서드)
python -m unittest tests.test_tokenizer.TestSingleTokens.test_string_token -v

# 스모크 테스트
python main.py
```

> 테스트 프레임워크는 표준 라이브러리 `unittest` 만 사용한다. `pytest` 등 외부 패키지 사용 금지.

---

## 목표 파일 구조

```
jsonparser/
├── main.py                  # 각 Phase 스모크 테스트 진입점
├── plan.md                  # 전체 구현 계획 및 단계 상태
├── docs/design/             # Phase별 설계 문서
│   ├── phase1-tokenizer.md
│   ├── phase2-parser.md
│   ├── phase3-type-conversion.md
│   ├── phase4-serializer.md
│   ├── phase5-file-io.md
│   ├── phase6-error-handling.md
│   └── phase7-testing.md
├── jsonparser/              # 라이브러리 패키지
│   ├── __init__.py          # load, loads, dump, dumps 공개 API
│   ├── tokenizer.py         # Phase 1
│   ├── parser.py            # Phase 2~3
│   ├── serializer.py        # Phase 4
│   ├── io.py                # Phase 5
│   └── exceptions.py        # Phase 6
└── tests/                   # Phase 7
    ├── test_tokenizer.py
    ├── test_parser.py
    ├── test_serializer.py
    ├── test_io.py
    ├── test_errors.py
    └── test_integration.py
```

---

## 아키텍처 개요

데이터 흐름:

```
문자열 입력
    │
    ▼
tokenizer.tokenize(text)          → list[Token]
    │
    ▼
parser.parse(tokens)              → Python 객체 (dict/list/str/int/float/bool/None)
    │
    ▼ (역방향)
serializer.dumps(obj, indent)     → JSON 문자열
    │
    ▼
io.dump(obj, fp) / io.load(fp)    → 파일 입출력 래퍼
```

- **Tokenizer**: 문자 수준 처리 전담. 이스케이프 해제, 숫자 타입 판별(int/float)을 여기서 수행.
- **Parser**: 재귀 하강 파서. `Token` 리스트를 소비하며 Python 네이티브 타입을 직접 반환. 별도 AST 없음.
- **Serializer**: `bool`을 `int`보다 먼저 분기해야 함 (`bool`은 `int` 서브클래스).
- **exceptions.py**: `JSONDecodeError(ValueError)` — Phase 6에서 도입. 그 전까지는 `ValueError`를 임시 사용.
- **io.py**: 파일 열기/닫기는 호출자 책임. 라이브러리는 `fp.read()` / `fp.write()` 만 사용.

---

## 설계 문서 위치

각 Phase 구현 전에 반드시 해당 설계 문서를 참고한다.

| Phase | 설계 문서 | 핵심 내용 |
|-------|----------|---------|
| 1 | `docs/design/phase1-tokenizer.md` | `TokenType` enum, `Token` dataclass, 이스케이프 표, 숫자 문법 |
| 2 | `docs/design/phase2-parser.md` | `Parser` 클래스, `parse_object` / `parse_array` 알고리즘 |
| 3 | `docs/design/phase3-type-conversion.md` | JSON → Python 타입 매핑, `\uXXXX` 처리 |
| 4 | `docs/design/phase4-serializer.md` | compact / pretty-print 출력 형식, `bool` 우선 분기 |
| 5 | `docs/design/phase5-file-io.md` | 4개 공개 API, `__init__.py` export |
| 6 | `docs/design/phase6-error-handling.md` | `JSONDecodeError` 정의, line/col 계산, 수정 범위 |
| 7 | `docs/design/phase7-testing.md` | 단위 / 통합 / 엣지케이스 테스트 목록 |

---

## 구현 원칙

- Phase 완료 기준은 각 설계 문서 말미의 체크리스트로 확인한다.
- 다음 Phase로 넘어가기 전에 `main.py` 스모크 테스트를 실행해 확인한다.
- Phase 6 이전까지 `ValueError`를 임시 예외로 사용하고, Phase 6에서 `JSONDecodeError`로 일괄 교체한다.
- `jsonparser/` 패키지의 공개 API는 `load`, `loads`, `dump`, `dumps` 4개만 노출한다.
