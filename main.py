from jsonparser.parser import parse_string

result = parse_string('{"name": "Alice", "scores": [10, 20.5], "active": true, "extra": null}')
print(result)

print(parse_string('[]'))
print(parse_string('42'))
print(parse_string('"hi"'))
