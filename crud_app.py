import os
import jsonparser

DB_FILE = "db.json"


# ── 파일 I/O ────────────────────────────────────────────────────────────────

def _load() -> list:
    if not os.path.exists(DB_FILE):
        return []
    with open(DB_FILE, encoding="utf-8") as fp:
        data = jsonparser.load(fp)
    return data if isinstance(data, list) else []


def _save(records: list) -> None:
    with open(DB_FILE, "w", encoding="utf-8") as fp:
        jsonparser.dump(records, fp, indent=2)


def _next_id(records: list) -> int:
    return max((r["id"] for r in records if "id" in r), default=0) + 1


# ── 출력 헬퍼 ───────────────────────────────────────────────────────────────

def _print_record(record: dict) -> None:
    print(jsonparser.dumps(record, indent=2))


def _print_table(records: list) -> None:
    if not records:
        print("  (데이터 없음)")
        return
    for r in records:
        fields = ", ".join(f"{k}: {v}" for k, v in r.items())
        print(f"  [{r.get('id', '?')}] {fields}")


# ── CRUD ────────────────────────────────────────────────────────────────────

def create() -> None:
    print("\n─── 새 데이터 추가 ───")
    records = _load()

    fields: dict = {}
    print("필드를 입력하세요. 빈 줄을 입력하면 종료합니다.")
    while True:
        key = input("  필드명: ").strip()
        if not key:
            break
        val = input(f"  {key} 값: ").strip()
        # 숫자 자동 변환
        if val.lstrip("-").isdigit():
            fields[key] = int(val)
        else:
            try:
                fields[key] = float(val)
            except ValueError:
                if val.lower() == "true":
                    fields[key] = True
                elif val.lower() == "false":
                    fields[key] = False
                elif val.lower() == "null":
                    fields[key] = None
                else:
                    fields[key] = val

    if not fields:
        print("필드가 없어 저장하지 않았습니다.")
        return

    new_id = _next_id(records)
    record = {"id": new_id, **fields}
    records.append(record)
    _save(records)
    print(f"\n저장 완료 (id={new_id})")
    _print_record(record)


def read() -> None:
    print("\n─── 목록 / 검색 ───")
    records = _load()

    keyword = input("검색어 입력 (id 또는 키=값, 빈 줄이면 전체): ").strip()

    if not keyword:
        print(f"\n전체 {len(records)}건")
        _print_table(records)
        return

    # id 검색
    if keyword.isdigit():
        target_id = int(keyword)
        results = [r for r in records if r.get("id") == target_id]
    # 키=값 검색
    elif "=" in keyword:
        k, _, v = keyword.partition("=")
        k, v = k.strip(), v.strip()
        results = [
            r for r in records
            if str(r.get(k, "")).lower() == v.lower()
        ]
    # 값 포함 검색
    else:
        results = [
            r for r in records
            if any(keyword.lower() in str(val).lower() for val in r.values())
        ]

    print(f"\n검색 결과 {len(results)}건")
    _print_table(results)


def update() -> None:
    print("\n─── 데이터 수정 ───")
    records = _load()
    _print_table(records)

    if not records:
        return

    try:
        target_id = int(input("\n수정할 id: ").strip())
    except ValueError:
        print("올바른 id를 입력하세요.")
        return

    idx = next((i for i, r in enumerate(records) if r.get("id") == target_id), None)
    if idx is None:
        print(f"id={target_id} 를 찾을 수 없습니다.")
        return

    record = records[idx]
    print("\n현재 데이터:")
    _print_record(record)

    print("\n수정할 필드와 값을 입력하세요. 빈 줄을 입력하면 종료합니다.")
    changed = False
    while True:
        key = input("  필드명: ").strip()
        if not key:
            break
        if key == "id":
            print("  id는 수정할 수 없습니다.")
            continue
        val = input(f"  {key} 값: ").strip()
        if val.lstrip("-").isdigit():
            record[key] = int(val)
        else:
            try:
                record[key] = float(val)
            except ValueError:
                if val.lower() == "true":
                    record[key] = True
                elif val.lower() == "false":
                    record[key] = False
                elif val.lower() == "null":
                    record[key] = None
                else:
                    record[key] = val
        changed = True

    if not changed:
        print("변경 사항 없음.")
        return

    records[idx] = record
    _save(records)
    print("\n수정 완료:")
    _print_record(record)


def delete() -> None:
    print("\n─── 데이터 삭제 ───")
    records = _load()
    _print_table(records)

    if not records:
        return

    try:
        target_id = int(input("\n삭제할 id: ").strip())
    except ValueError:
        print("올바른 id를 입력하세요.")
        return

    idx = next((i for i, r in enumerate(records) if r.get("id") == target_id), None)
    if idx is None:
        print(f"id={target_id} 를 찾을 수 없습니다.")
        return

    record = records[idx]
    print("\n삭제 대상:")
    _print_record(record)

    confirm = input("\n정말 삭제하시겠습니까? (y/N): ").strip().lower()
    if confirm != "y":
        print("취소했습니다.")
        return

    records.pop(idx)
    _save(records)
    print(f"id={target_id} 삭제 완료.")


# ── 메인 루프 ────────────────────────────────────────────────────────────────

MENU = """
==============================
  JSON CRUD 콘솔 애플리케이션
==============================
  1. 전체 목록 / 검색  (Read)
  2. 새 데이터 추가   (Create)
  3. 데이터 수정      (Update)
  4. 데이터 삭제      (Delete)
  0. 종료
=============================="""


def main() -> None:
    print(f"저장소: {os.path.abspath(DB_FILE)}")
    while True:
        print(MENU)
        choice = input("선택: ").strip()
        if choice == "1":
            read()
        elif choice == "2":
            create()
        elif choice == "3":
            update()
        elif choice == "4":
            delete()
        elif choice == "0":
            print("종료합니다.")
            break
        else:
            print("1~4 또는 0을 입력하세요.")


if __name__ == "__main__":
    main()
