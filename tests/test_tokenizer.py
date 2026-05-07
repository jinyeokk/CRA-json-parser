import unittest
from jsonparser.tokenizer import tokenize, TokenType


class TestStructuralTokens(unittest.TestCase):

    def test_structural_chars(self):
        pairs = [
            ('{', TokenType.LBRACE),
            ('}', TokenType.RBRACE),
            ('[', TokenType.LBRACKET),
            (']', TokenType.RBRACKET),
            (':', TokenType.COLON),
            (',', TokenType.COMMA),
        ]
        for src, expected in pairs:
            with self.subTest(src=src):
                self.assertEqual(tokenize(src)[0].type, expected)

    def test_eof_always_last(self):
        tokens = tokenize('{}')
        self.assertEqual(tokens[-1].type, TokenType.EOF)
        self.assertIsNone(tokens[-1].value)


class TestStringToken(unittest.TestCase):

    def test_simple_string(self):
        t = tokenize('"hello"')[0]
        self.assertEqual(t.type, TokenType.STRING)
        self.assertEqual(t.value, 'hello')

    def test_empty_string(self):
        t = tokenize('""')[0]
        self.assertEqual(t.type, TokenType.STRING)
        self.assertEqual(t.value, '')

    def test_escape_quote(self):
        t = tokenize(r'"say \"hi\""')[0]
        self.assertEqual(t.value, 'say "hi"')

    def test_escape_backslash(self):
        t = tokenize(r'"\\"')[0]
        self.assertEqual(t.value, '\\')

    def test_escape_newline(self):
        t = tokenize(r'"\n"')[0]
        self.assertEqual(t.value, '\n')

    def test_escape_tab(self):
        t = tokenize(r'"\t"')[0]
        self.assertEqual(t.value, '\t')

    def test_escape_slash(self):
        t = tokenize(r'"\/"')[0]
        self.assertEqual(t.value, '/')

    def test_escape_backspace(self):
        t = tokenize(r'"\b"')[0]
        self.assertEqual(t.value, '\b')

    def test_escape_formfeed(self):
        t = tokenize(r'"\f"')[0]
        self.assertEqual(t.value, '\f')

    def test_escape_carriage_return(self):
        t = tokenize(r'"\r"')[0]
        self.assertEqual(t.value, '\r')

    def test_unicode_escape(self):
        t = tokenize(r'"A"')[0]
        self.assertEqual(t.value, 'A')

    def test_unicode_escape_korean(self):
        t = tokenize(r'"한"')[0]
        self.assertEqual(t.value, '한')


class TestNumberToken(unittest.TestCase):

    def test_integer(self):
        t = tokenize('42')[0]
        self.assertEqual(t.value, 42)
        self.assertIsInstance(t.value, int)

    def test_zero(self):
        t = tokenize('0')[0]
        self.assertEqual(t.value, 0)
        self.assertIsInstance(t.value, int)

    def test_negative_integer(self):
        t = tokenize('-7')[0]
        self.assertEqual(t.value, -7)
        self.assertIsInstance(t.value, int)

    def test_float(self):
        t = tokenize('3.14')[0]
        self.assertAlmostEqual(t.value, 3.14)
        self.assertIsInstance(t.value, float)

    def test_exponent_lower(self):
        t = tokenize('1e3')[0]
        self.assertAlmostEqual(t.value, 1000.0)
        self.assertIsInstance(t.value, float)

    def test_exponent_upper(self):
        t = tokenize('1E3')[0]
        self.assertAlmostEqual(t.value, 1000.0)

    def test_negative_exponent(self):
        t = tokenize('1e-2')[0]
        self.assertAlmostEqual(t.value, 0.01)

    def test_float_with_exponent(self):
        t = tokenize('1.5e2')[0]
        self.assertAlmostEqual(t.value, 150.0)


class TestLiteralTokens(unittest.TestCase):

    def test_true(self):
        t = tokenize('true')[0]
        self.assertEqual(t.type, TokenType.TRUE)
        self.assertEqual(t.value, 'true')

    def test_false(self):
        t = tokenize('false')[0]
        self.assertEqual(t.type, TokenType.FALSE)
        self.assertEqual(t.value, 'false')

    def test_null(self):
        t = tokenize('null')[0]
        self.assertEqual(t.type, TokenType.NULL)
        self.assertEqual(t.value, 'null')


class TestWhitespace(unittest.TestCase):

    def test_whitespace_ignored(self):
        tokens = tokenize('  {  }  ')
        types = [t.type for t in tokens]
        self.assertEqual(types, [TokenType.LBRACE, TokenType.RBRACE, TokenType.EOF])

    def test_newline_and_tab_ignored(self):
        tokens = tokenize('\n{\t}\r')
        types = [t.type for t in tokens]
        self.assertEqual(types, [TokenType.LBRACE, TokenType.RBRACE, TokenType.EOF])


class TestPosition(unittest.TestCase):

    def test_pos_tracked(self):
        tokens = tokenize('{"key": 1}')
        self.assertEqual(tokens[0].pos, 0)   # {
        self.assertEqual(tokens[1].pos, 1)   # "key"
        self.assertEqual(tokens[2].pos, 6)   # :
        self.assertEqual(tokens[3].pos, 8)   # 1


class TestTokenizerErrors(unittest.TestCase):

    def test_unterminated_string(self):
        with self.assertRaises(ValueError) as ctx:
            tokenize('"no end')
        self.assertIn('Unterminated', str(ctx.exception))

    def test_invalid_escape(self):
        with self.assertRaises(ValueError) as ctx:
            tokenize('"\\q"')
        self.assertIn('escape', str(ctx.exception))

    def test_invalid_unicode_escape(self):
        with self.assertRaises(ValueError) as ctx:
            tokenize('"\\uXXXX"')
        self.assertIn('uXXXX', str(ctx.exception))

    def test_unexpected_character(self):
        with self.assertRaises(ValueError) as ctx:
            tokenize('@')
        self.assertIn('Unexpected character', str(ctx.exception))

    def test_invalid_literal(self):
        with self.assertRaises(ValueError):
            tokenize('tru')


if __name__ == '__main__':
    unittest.main()
