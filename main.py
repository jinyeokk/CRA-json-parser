from jsonparser.tokenizer import tokenize

tokens = tokenize('{"key": [1, true, null]}')
for t in tokens:
    print(t)
