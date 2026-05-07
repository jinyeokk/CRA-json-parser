import unittest
from jsonparser.serializer import dumps


class TestSerializerCompact(unittest.TestCase):

    def test_empty_object(self):
        self.assertEqual(dumps({}), '{}')

    def test_empty_array(self):
        self.assertEqual(dumps([]), '[]')

    def test_object(self):
        self.assertEqual(dumps({"a": 1}), '{"a":1}')

    def test_array(self):
        self.assertEqual(dumps([1, 2, 3]), '[1,2,3]')

    def test_nested(self):
        self.assertEqual(dumps({"a": [1, 2]}), '{"a":[1,2]}')

    def test_multiple_keys(self):
        self.assertEqual(dumps({"a": 1, "b": 2}), '{"a":1,"b":2}')


class TestSerializerPretty(unittest.TestCase):

    def test_object_indent2(self):
        result = dumps({"a": 1}, indent=2)
        self.assertEqual(result, '{\n  "a": 1\n}')

    def test_array_indent2(self):
        result = dumps([1, 2], indent=2)
        self.assertEqual(result, '[\n  1,\n  2\n]')

    def test_nested_indent4(self):
        obj = {"arr": [1, 2]}
        expected = '{\n    "arr": [\n        1,\n        2\n    ]\n}'
        self.assertEqual(dumps(obj, indent=4), expected)


class TestSerializerTypes(unittest.TestCase):

    def test_string(self):
        self.assertEqual(dumps("hello"), '"hello"')

    def test_integer(self):
        self.assertEqual(dumps(42), '42')

    def test_negative_integer(self):
        self.assertEqual(dumps(-7), '-7')

    def test_float(self):
        self.assertEqual(dumps(3.14), '3.14')

    def test_true(self):
        self.assertEqual(dumps(True), 'true')

    def test_false(self):
        self.assertEqual(dumps(False), 'false')

    def test_none(self):
        self.assertEqual(dumps(None), 'null')

    def test_bool_not_int(self):
        self.assertEqual(dumps({"v": True}), '{"v":true}')
        self.assertEqual(dumps({"v": 1}),    '{"v":1}')


class TestSerializerStringEscape(unittest.TestCase):

    def test_escape_quote(self):
        self.assertEqual(dumps('say "hi"'), '"say \\"hi\\""')

    def test_escape_backslash(self):
        self.assertEqual(dumps('a\\b'), '"a\\\\b"')

    def test_escape_newline(self):
        self.assertEqual(dumps("a\nb"), '"a\\nb"')

    def test_escape_tab(self):
        self.assertEqual(dumps("a\tb"), '"a\\tb"')

    def test_escape_carriage_return(self):
        self.assertEqual(dumps("a\rb"), '"a\\rb"')


class TestSerializerErrors(unittest.TestCase):

    def test_inf_raises(self):
        with self.assertRaises(ValueError):
            dumps(float('inf'))

    def test_nan_raises(self):
        with self.assertRaises(ValueError):
            dumps(float('nan'))

    def test_unsupported_type(self):
        with self.assertRaises(TypeError):
            dumps(object())

    def test_non_string_dict_key(self):
        with self.assertRaises(TypeError):
            dumps({1: "v"})


if __name__ == '__main__':
    unittest.main()
