import unittest
from jsonparser.parser import parse_string


class TestParserObject(unittest.TestCase):

    def test_empty_object(self):
        self.assertEqual(parse_string('{}'), {})

    def test_single_key(self):
        self.assertEqual(parse_string('{"a": 1}'), {"a": 1})

    def test_multiple_keys(self):
        result = parse_string('{"a": 1, "b": 2}')
        self.assertEqual(result, {"a": 1, "b": 2})

    def test_nested_object(self):
        result = parse_string('{"a": {"b": 1}}')
        self.assertEqual(result, {"a": {"b": 1}})


class TestParserArray(unittest.TestCase):

    def test_empty_array(self):
        self.assertEqual(parse_string('[]'), [])

    def test_single_element(self):
        self.assertEqual(parse_string('[1]'), [1])

    def test_multiple_elements(self):
        self.assertEqual(parse_string('[1, 2, 3]'), [1, 2, 3])

    def test_nested_array(self):
        self.assertEqual(parse_string('[[1, 2], [3]]'), [[1, 2], [3]])

    def test_mixed_elements(self):
        result = parse_string('[1, "two", null, false]')
        self.assertEqual(result, [1, "two", None, False])


class TestParserNested(unittest.TestCase):

    def test_object_in_array(self):
        result = parse_string('[{"a": 1}]')
        self.assertEqual(result, [{"a": 1}])

    def test_array_in_object(self):
        result = parse_string('{"a": [1, 2]}')
        self.assertEqual(result, {"a": [1, 2]})

    def test_deeply_nested(self):
        result = parse_string('{"a": [1, {"b": null}]}')
        self.assertEqual(result, {"a": [1, {"b": None}]})


class TestParserTypes(unittest.TestCase):

    def test_integer(self):
        self.assertEqual(parse_string('42'), 42)
        self.assertIsInstance(parse_string('42'), int)

    def test_negative_integer(self):
        self.assertEqual(parse_string('-7'), -7)

    def test_float(self):
        self.assertAlmostEqual(parse_string('3.14'), 3.14)
        self.assertIsInstance(parse_string('3.14'), float)

    def test_exponent(self):
        self.assertAlmostEqual(parse_string('1e3'), 1000.0)

    def test_string(self):
        self.assertEqual(parse_string('"hello"'), 'hello')

    def test_true(self):
        self.assertIs(parse_string('true'), True)

    def test_false(self):
        self.assertIs(parse_string('false'), False)

    def test_null(self):
        self.assertIsNone(parse_string('null'))

    def test_bool_is_not_int(self):
        self.assertIs(type(parse_string('true')), bool)
        self.assertIs(type(parse_string('false')), bool)


class TestParserErrors(unittest.TestCase):

    def test_non_string_key(self):
        with self.assertRaises(ValueError):
            parse_string('{1: "v"}')

    def test_missing_colon(self):
        with self.assertRaises(ValueError):
            parse_string('{"k" "v"}')

    def test_trailing_comma_object(self):
        with self.assertRaises(ValueError):
            parse_string('{"k": 1,}')

    def test_trailing_comma_array(self):
        with self.assertRaises(ValueError):
            parse_string('[1,]')

    def test_missing_closing_brace(self):
        with self.assertRaises(ValueError):
            parse_string('{"k": 1')

    def test_missing_closing_bracket(self):
        with self.assertRaises(ValueError):
            parse_string('[1, 2')

    def test_extra_data(self):
        with self.assertRaises(ValueError):
            parse_string('{} {}')


if __name__ == '__main__':
    unittest.main()
