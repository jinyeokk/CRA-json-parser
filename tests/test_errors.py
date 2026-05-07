import unittest
import jsonparser
from jsonparser.exceptions import JSONDecodeError


class TestJSONDecodeErrorClass(unittest.TestCase):

    def test_is_value_error_subclass(self):
        self.assertTrue(issubclass(JSONDecodeError, ValueError))

    def test_caught_as_value_error(self):
        with self.assertRaises(ValueError):
            jsonparser.loads('{bad}')

    def test_caught_as_json_decode_error(self):
        with self.assertRaises(JSONDecodeError):
            jsonparser.loads('{bad}')


class TestErrorPosition(unittest.TestCase):

    def test_lineno_colno(self):
        try:
            jsonparser.loads('\n{"key": @}')
            self.fail("JSONDecodeError가 발생해야 함")
        except JSONDecodeError as e:
            self.assertEqual(e.lineno, 2)
            self.assertEqual(e.colno,  9)

    def test_pos_attribute(self):
        try:
            jsonparser.loads('@')
            self.fail("JSONDecodeError가 발생해야 함")
        except JSONDecodeError as e:
            self.assertEqual(e.pos, 0)

    def test_doc_attribute(self):
        src = '{"bad": @}'
        try:
            jsonparser.loads(src)
            self.fail("JSONDecodeError가 발생해야 함")
        except JSONDecodeError as e:
            self.assertEqual(e.doc, src)


class TestTokenizerErrors(unittest.TestCase):

    def test_unexpected_character(self):
        with self.assertRaises(JSONDecodeError) as ctx:
            jsonparser.loads('@')
        self.assertIn('Unexpected character', str(ctx.exception))

    def test_unterminated_string(self):
        with self.assertRaises(JSONDecodeError) as ctx:
            jsonparser.loads('"no end')
        self.assertIn('Unterminated', str(ctx.exception))

    def test_invalid_escape(self):
        with self.assertRaises(JSONDecodeError):
            jsonparser.loads('"\\q"')


class TestParserErrors(unittest.TestCase):

    def test_non_string_key(self):
        with self.assertRaises(JSONDecodeError):
            jsonparser.loads('{1: "v"}')

    def test_missing_colon(self):
        with self.assertRaises(JSONDecodeError):
            jsonparser.loads('{"k" "v"}')

    def test_missing_value(self):
        with self.assertRaises(JSONDecodeError):
            jsonparser.loads('{"k": }')

    def test_extra_data(self):
        with self.assertRaises(JSONDecodeError) as ctx:
            jsonparser.loads('{}{}')
        self.assertIn('Extra data', str(ctx.exception))

    def test_unexpected_eof(self):
        with self.assertRaises(JSONDecodeError):
            jsonparser.loads('{"k":')


if __name__ == '__main__':
    unittest.main()
