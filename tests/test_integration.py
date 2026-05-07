import unittest
import jsonparser


COMPLEX = {
    "string":  'hello "world"\nnewline',
    "int":     -42,
    "float":   3.14,
    "bool_t":  True,
    "bool_f":  False,
    "null":    None,
    "array":   [1, "two", None, False],
    "nested":  {"a": {"b": {"c": 99}}},
    "unicode": "한글 テスト",
}


class TestRoundtrip(unittest.TestCase):

    def test_roundtrip_compact(self):
        self.assertEqual(jsonparser.loads(jsonparser.dumps(COMPLEX)), COMPLEX)

    def test_roundtrip_pretty(self):
        self.assertEqual(jsonparser.loads(jsonparser.dumps(COMPLEX, indent=2)), COMPLEX)

    def test_roundtrip_indent4(self):
        self.assertEqual(jsonparser.loads(jsonparser.dumps(COMPLEX, indent=4)), COMPLEX)


class TestEdgeCases(unittest.TestCase):

    def test_empty_object(self):
        self.assertEqual(jsonparser.loads('{}'), {})

    def test_empty_array(self):
        self.assertEqual(jsonparser.loads('[]'), [])

    def test_empty_string(self):
        self.assertEqual(jsonparser.loads('""'), '')

    def test_zero(self):
        self.assertEqual(jsonparser.loads('0'), 0)

    def test_negative_zero(self):
        self.assertEqual(jsonparser.loads('-0'), 0)

    def test_large_exponent(self):
        self.assertAlmostEqual(jsonparser.loads('1e100'), 1e100)

    def test_chinese(self):
        self.assertEqual(jsonparser.loads('"中文"'), '中文')

    def test_korean(self):
        self.assertEqual(jsonparser.loads('"한글"'), '한글')

    def test_deeply_nested(self):
        obj = {"a": {"b": {"c": {"d": [1, 2, 3]}}}}
        self.assertEqual(jsonparser.loads(jsonparser.dumps(obj)), obj)

    def test_unicode_escape_roundtrip(self):
        result = jsonparser.loads(r'"A"')
        self.assertEqual(result, 'A')


if __name__ == '__main__':
    unittest.main()
