import jsonparser
from jsonparser.exceptions import JSONDecodeError

bad_inputs = [
    ('{"key": @}',     "Unexpected character"),
    ('{"key": "val}',  "Unterminated string"),
    ('{1: "val"}',     "Object key must be a string"),
    ('{"k": }',        "Unexpected token"),
    ('{"k": 1} extra', "Extra data"),
]

for src, expected_msg in bad_inputs:
    try:
        jsonparser.loads(src)
        print(f"FAIL: 오류가 발생해야 함 → {src!r}")
    except JSONDecodeError as e:
        print(f"OK  ({expected_msg}): {e}")
