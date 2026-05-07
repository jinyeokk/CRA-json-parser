import os
import tempfile
import unittest
import jsonparser


class TestLoads(unittest.TestCase):

    def test_object(self):
        self.assertEqual(jsonparser.loads('{"x": 1}'), {"x": 1})

    def test_array(self):
        self.assertEqual(jsonparser.loads('[1, 2]'), [1, 2])

    def test_string(self):
        self.assertEqual(jsonparser.loads('"hello"'), 'hello')

    def test_number(self):
        self.assertEqual(jsonparser.loads('42'), 42)

    def test_bool(self):
        self.assertIs(jsonparser.loads('true'), True)

    def test_null(self):
        self.assertIsNone(jsonparser.loads('null'))


class TestDumps(unittest.TestCase):

    def test_compact(self):
        self.assertEqual(jsonparser.dumps({"x": 1}), '{"x":1}')

    def test_pretty(self):
        result = jsonparser.dumps({"x": 1}, indent=2)
        self.assertEqual(result, '{\n  "x": 1\n}')


class TestLoadFile(unittest.TestCase):

    def _write_temp(self, content):
        f = tempfile.NamedTemporaryFile(
            mode='w', suffix='.json', encoding='utf-8', delete=False
        )
        f.write(content)
        f.close()
        return f.name

    def test_load_object(self):
        path = self._write_temp('{"x": 1}')
        try:
            with open(path, encoding='utf-8') as fp:
                self.assertEqual(jsonparser.load(fp), {"x": 1})
        finally:
            os.unlink(path)

    def test_load_array(self):
        path = self._write_temp('[1, 2, 3]')
        try:
            with open(path, encoding='utf-8') as fp:
                self.assertEqual(jsonparser.load(fp), [1, 2, 3])
        finally:
            os.unlink(path)


class TestDumpFile(unittest.TestCase):

    def test_dump_compact(self):
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        try:
            with open(path, 'w', encoding='utf-8') as fp:
                jsonparser.dump({"x": 1}, fp)
            with open(path, encoding='utf-8') as fp:
                self.assertEqual(fp.read(), '{"x":1}')
        finally:
            os.unlink(path)

    def test_dump_pretty(self):
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        try:
            with open(path, 'w', encoding='utf-8') as fp:
                jsonparser.dump({"x": 1}, fp, indent=2)
            with open(path, encoding='utf-8') as fp:
                self.assertEqual(fp.read(), '{\n  "x": 1\n}')
        finally:
            os.unlink(path)


class TestRoundtrip(unittest.TestCase):

    def test_roundtrip_compact(self):
        obj = {"name": "Alice", "scores": [10, 20], "active": True, "extra": None}
        self.assertEqual(jsonparser.loads(jsonparser.dumps(obj)), obj)

    def test_roundtrip_pretty(self):
        obj = {"name": "Alice", "scores": [10, 20], "active": True, "extra": None}
        self.assertEqual(jsonparser.loads(jsonparser.dumps(obj, indent=2)), obj)

    def test_roundtrip_file(self):
        obj = {"name": "Alice", "scores": [10, 20], "active": True}
        fd, path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        try:
            with open(path, 'w', encoding='utf-8') as fp:
                jsonparser.dump(obj, fp, indent=2)
            with open(path, encoding='utf-8') as fp:
                self.assertEqual(jsonparser.load(fp), obj)
        finally:
            os.unlink(path)


if __name__ == '__main__':
    unittest.main()
