import jsonparser

src = '{"name": "Alice", "scores": [10, 20], "active": true}'
obj = jsonparser.loads(src)
print(obj)
print(jsonparser.dumps(obj))

with open("output.json", "w", encoding="utf-8") as f:
    jsonparser.dump(obj, f, indent=2)

with open("output.json", encoding="utf-8") as f:
    loaded = jsonparser.load(f)

assert loaded == obj
print("파일 입출력 테스트 통과")
