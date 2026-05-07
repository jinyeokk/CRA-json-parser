from .tokenizer import tokenize, Token, TokenType
from .exceptions import JSONDecodeError


class Parser:
    def __init__(self, tokens: list, text: str = ''):
        self.tokens = tokens
        self.text   = text
        self.pos    = 0

    def peek(self) -> Token:
        return self.tokens[self.pos]

    def consume(self) -> Token:
        token = self.tokens[self.pos]
        self.pos += 1
        return token

    def expect(self, token_type: TokenType) -> Token:
        token = self.peek()
        if token.type != token_type:
            raise JSONDecodeError(
                f"Expected {token_type.name}, got {token.type.name}",
                self.text, token.pos
            )
        return self.consume()

    def parse_value(self) -> object:
        token = self.peek()

        if token.type == TokenType.LBRACE:
            return self.parse_object()
        if token.type == TokenType.LBRACKET:
            return self.parse_array()
        if token.type == TokenType.STRING:
            return self.consume().value
        if token.type == TokenType.NUMBER:
            return self.consume().value
        if token.type == TokenType.TRUE:
            self.consume()
            return True
        if token.type == TokenType.FALSE:
            self.consume()
            return False
        if token.type == TokenType.NULL:
            self.consume()
            return None
        if token.type == TokenType.EOF:
            raise JSONDecodeError("Unexpected end of input", self.text, token.pos)

        raise JSONDecodeError(
            f"Unexpected token {token.type.name}", self.text, token.pos
        )

    def parse_object(self) -> dict:
        self.expect(TokenType.LBRACE)
        result = {}

        if self.peek().type == TokenType.RBRACE:
            self.consume()
            return result

        while True:
            key_token = self.peek()
            if key_token.type != TokenType.STRING:
                raise JSONDecodeError(
                    f"Object key must be a string, got {key_token.type.name}",
                    self.text, key_token.pos
                )
            key = self.consume().value
            self.expect(TokenType.COLON)
            result[key] = self.parse_value()

            next_token = self.peek()
            if next_token.type == TokenType.COMMA:
                self.consume()
                if self.peek().type == TokenType.RBRACE:
                    raise JSONDecodeError(
                        "Trailing comma in object", self.text, self.peek().pos
                    )
            elif next_token.type == TokenType.RBRACE:
                self.consume()
                return result
            else:
                raise JSONDecodeError(
                    "Expected ',' or '}' in object", self.text, next_token.pos
                )

    def parse_array(self) -> list:
        self.expect(TokenType.LBRACKET)
        result = []

        if self.peek().type == TokenType.RBRACKET:
            self.consume()
            return result

        while True:
            result.append(self.parse_value())

            next_token = self.peek()
            if next_token.type == TokenType.COMMA:
                self.consume()
                if self.peek().type == TokenType.RBRACKET:
                    raise JSONDecodeError(
                        "Trailing comma in array", self.text, self.peek().pos
                    )
            elif next_token.type == TokenType.RBRACKET:
                self.consume()
                return result
            else:
                raise JSONDecodeError(
                    "Expected ',' or ']' in array", self.text, next_token.pos
                )


def parse(tokens: list, text: str = '') -> object:
    parser = Parser(tokens, text)
    value  = parser.parse_value()

    remaining = parser.peek()
    if remaining.type != TokenType.EOF:
        raise JSONDecodeError(
            "Extra data after end of JSON", text, remaining.pos
        )

    return value


def parse_string(text: str) -> object:
    return parse(tokenize(text), text)
