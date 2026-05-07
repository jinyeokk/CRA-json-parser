from jsonparser.serializer import dumps

obj = {
    "name": "Alice",
    "scores": [10, 20.5],
    "active": True,
    "extra": None,
}

print(dumps(obj))
print(dumps(obj, indent=2))
