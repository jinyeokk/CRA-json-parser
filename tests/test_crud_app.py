import os
import sys
import tempfile
import unittest
import unittest.mock as mock

sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
import crud_app
import jsonparser


def fake_input(values):
    it = iter(values)
    def _input(_=''):
        try:
            return next(it)
        except StopIteration:
            return ''
    return _input


class CRUDTestBase(unittest.TestCase):
    """각 테스트마다 독립된 임시 DB 파일 사용."""

    def setUp(self):
        fd, self.db_path = tempfile.mkstemp(suffix='.json')
        os.close(fd)
        os.unlink(self.db_path)          # 빈 상태로 시작
        crud_app.DB_FILE = self.db_path

    def tearDown(self):
        if os.path.exists(self.db_path):
            os.unlink(self.db_path)

    def _records(self):
        return crud_app._load()


# ── Create ───────────────────────────────────────────────────────────────────

class TestCreate(CRUDTestBase):

    def test_create_basic(self):
        with mock.patch('builtins.input', fake_input(['name', 'Alice', 'age', '30', ''])):
            crud_app.create()
        records = self._records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Alice')
        self.assertEqual(records[0]['age'], 30)

    def test_create_auto_id_starts_at_1(self):
        with mock.patch('builtins.input', fake_input(['name', 'Alice', ''])):
            crud_app.create()
        self.assertEqual(self._records()[0]['id'], 1)

    def test_create_auto_id_increments(self):
        for name in ['Alice', 'Bob', 'Charlie']:
            with mock.patch('builtins.input', fake_input(['name', name, ''])):
                crud_app.create()
        ids = [r['id'] for r in self._records()]
        self.assertEqual(ids, [1, 2, 3])

    def test_create_empty_fields_not_saved(self):
        with mock.patch('builtins.input', fake_input([''])):
            crud_app.create()
        self.assertEqual(len(self._records()), 0)

    def test_create_type_int(self):
        with mock.patch('builtins.input', fake_input(['score', '42', ''])):
            crud_app.create()
        val = self._records()[0]['score']
        self.assertIsInstance(val, int)
        self.assertEqual(val, 42)

    def test_create_type_negative_int(self):
        with mock.patch('builtins.input', fake_input(['val', '-7', ''])):
            crud_app.create()
        self.assertEqual(self._records()[0]['val'], -7)

    def test_create_type_float(self):
        with mock.patch('builtins.input', fake_input(['score', '3.14', ''])):
            crud_app.create()
        val = self._records()[0]['score']
        self.assertIsInstance(val, float)
        self.assertAlmostEqual(val, 3.14)

    def test_create_type_bool_true(self):
        with mock.patch('builtins.input', fake_input(['active', 'true', ''])):
            crud_app.create()
        self.assertIs(self._records()[0]['active'], True)

    def test_create_type_bool_false(self):
        with mock.patch('builtins.input', fake_input(['active', 'false', ''])):
            crud_app.create()
        self.assertIs(self._records()[0]['active'], False)

    def test_create_type_null(self):
        with mock.patch('builtins.input', fake_input(['extra', 'null', ''])):
            crud_app.create()
        self.assertIsNone(self._records()[0]['extra'])

    def test_create_type_string(self):
        with mock.patch('builtins.input', fake_input(['city', 'Seoul', ''])):
            crud_app.create()
        self.assertEqual(self._records()[0]['city'], 'Seoul')

    def test_create_persists_to_file(self):
        with mock.patch('builtins.input', fake_input(['name', 'Alice', ''])):
            crud_app.create()
        with open(self.db_path, encoding='utf-8') as fp:
            data = jsonparser.load(fp)
        self.assertEqual(data[0]['name'], 'Alice')


# ── Read ─────────────────────────────────────────────────────────────────────

class TestRead(CRUDTestBase):

    def setUp(self):
        super().setUp()
        for name, age in [('Alice', 30), ('Bob', 25), ('Charlie', 35)]:
            with mock.patch('builtins.input', fake_input(['name', name, 'age', str(age), ''])):
                crud_app.create()

    def _captured_read(self, inputs):
        output = []
        with mock.patch('builtins.input', fake_input(inputs)):
            with mock.patch('builtins.print', side_effect=lambda *a, **k: output.append(' '.join(str(x) for x in a))):
                crud_app.read()
        return '\n'.join(output)

    def test_read_all(self):
        out = self._captured_read([''])
        self.assertIn('Alice', out)
        self.assertIn('Bob', out)
        self.assertIn('Charlie', out)

    def test_read_all_count(self):
        out = self._captured_read([''])
        self.assertIn('3', out)

    def test_read_by_id(self):
        out = self._captured_read(['2'])
        self.assertIn('Bob', out)
        self.assertNotIn('Alice', out)
        self.assertNotIn('Charlie', out)

    def test_read_by_key_value(self):
        out = self._captured_read(['name=Alice'])
        self.assertIn('Alice', out)
        self.assertNotIn('Bob', out)

    def test_read_by_keyword(self):
        out = self._captured_read(['Charlie'])
        self.assertIn('Charlie', out)
        self.assertNotIn('Alice', out)

    def test_read_no_result(self):
        out = self._captured_read(['name=Nobody'])
        self.assertIn('0', out)

    def test_read_empty_db(self):
        os.unlink(self.db_path)
        out = self._captured_read([''])
        self.assertIn('0', out)

    def test_read_id_case_insensitive_key_value(self):
        out = self._captured_read(['name=alice'])
        self.assertIn('Alice', out)


# ── Update ───────────────────────────────────────────────────────────────────

class TestUpdate(CRUDTestBase):

    def setUp(self):
        super().setUp()
        with mock.patch('builtins.input', fake_input(['name', 'Alice', 'age', '30', ''])):
            crud_app.create()
        with mock.patch('builtins.input', fake_input(['name', 'Bob', 'age', '25', ''])):
            crud_app.create()

    def test_update_field(self):
        with mock.patch('builtins.input', fake_input(['1', 'age', '31', ''])):
            crud_app.update()
        self.assertEqual(self._records()[0]['age'], 31)

    def test_update_adds_new_field(self):
        with mock.patch('builtins.input', fake_input(['1', 'email', 'alice@example.com', ''])):
            crud_app.update()
        self.assertEqual(self._records()[0]['email'], 'alice@example.com')

    def test_update_id_cannot_be_changed(self):
        with mock.patch('builtins.input', fake_input(['1', 'id', '99', ''])):
            crud_app.update()
        self.assertEqual(self._records()[0]['id'], 1)

    def test_update_nonexistent_id(self):
        with mock.patch('builtins.input', fake_input(['99', ''])):
            crud_app.update()
        records = self._records()
        self.assertEqual(len(records), 2)

    def test_update_no_change(self):
        with mock.patch('builtins.input', fake_input(['1', ''])):
            crud_app.update()
        self.assertEqual(self._records()[0]['age'], 30)

    def test_update_invalid_id_input(self):
        with mock.patch('builtins.input', fake_input(['abc'])):
            crud_app.update()
        self.assertEqual(len(self._records()), 2)

    def test_update_persists(self):
        with mock.patch('builtins.input', fake_input(['1', 'name', 'Alicia', ''])):
            crud_app.update()
        with open(self.db_path, encoding='utf-8') as fp:
            data = jsonparser.load(fp)
        self.assertEqual(data[0]['name'], 'Alicia')


# ── Delete ───────────────────────────────────────────────────────────────────

class TestDelete(CRUDTestBase):

    def setUp(self):
        super().setUp()
        for name in ['Alice', 'Bob', 'Charlie']:
            with mock.patch('builtins.input', fake_input(['name', name, ''])):
                crud_app.create()

    def test_delete_confirmed(self):
        with mock.patch('builtins.input', fake_input(['2', 'y'])):
            crud_app.delete()
        records = self._records()
        self.assertEqual(len(records), 2)
        self.assertTrue(all(r['id'] != 2 for r in records))

    def test_delete_cancelled(self):
        with mock.patch('builtins.input', fake_input(['2', 'n'])):
            crud_app.delete()
        self.assertEqual(len(self._records()), 3)

    def test_delete_cancelled_uppercase_N(self):
        with mock.patch('builtins.input', fake_input(['2', 'N'])):
            crud_app.delete()
        self.assertEqual(len(self._records()), 3)

    def test_delete_nonexistent_id(self):
        with mock.patch('builtins.input', fake_input(['99', 'y'])):
            crud_app.delete()
        self.assertEqual(len(self._records()), 3)

    def test_delete_invalid_id_input(self):
        with mock.patch('builtins.input', fake_input(['abc'])):
            crud_app.delete()
        self.assertEqual(len(self._records()), 3)

    def test_delete_remaining_ids_intact(self):
        with mock.patch('builtins.input', fake_input(['2', 'y'])):
            crud_app.delete()
        ids = [r['id'] for r in self._records()]
        self.assertIn(1, ids)
        self.assertIn(3, ids)

    def test_delete_persists(self):
        with mock.patch('builtins.input', fake_input(['1', 'y'])):
            crud_app.delete()
        with open(self.db_path, encoding='utf-8') as fp:
            data = jsonparser.load(fp)
        self.assertTrue(all(r['id'] != 1 for r in data))


# ── 파일 I/O 및 jsonparser 연동 ──────────────────────────────────────────────

class TestPersistence(CRUDTestBase):

    def test_db_file_created_on_first_create(self):
        self.assertFalse(os.path.exists(self.db_path))
        with mock.patch('builtins.input', fake_input(['name', 'Alice', ''])):
            crud_app.create()
        self.assertTrue(os.path.exists(self.db_path))

    def test_db_file_is_valid_json(self):
        with mock.patch('builtins.input', fake_input(['name', 'Alice', 'age', '30', ''])):
            crud_app.create()
        with open(self.db_path, encoding='utf-8') as fp:
            data = jsonparser.load(fp)
        self.assertIsInstance(data, list)

    def test_full_roundtrip(self):
        """Create → Update → Delete 후 파일 상태 검증."""
        with mock.patch('builtins.input', fake_input(['name', 'Alice', 'age', '30', ''])):
            crud_app.create()
        with mock.patch('builtins.input', fake_input(['name', 'Bob', 'age', '25', ''])):
            crud_app.create()
        with mock.patch('builtins.input', fake_input(['1', 'age', '31', ''])):
            crud_app.update()
        with mock.patch('builtins.input', fake_input(['2', 'y'])):
            crud_app.delete()

        records = self._records()
        self.assertEqual(len(records), 1)
        self.assertEqual(records[0]['name'], 'Alice')
        self.assertEqual(records[0]['age'], 31)


if __name__ == '__main__':
    unittest.main()
