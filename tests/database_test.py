import unittest

from src.api.database import ClickHouseDB
from src.api.models.work import CreativeWork

ITEM = {
    "DOI": "10.5840/ancientphil201434222",
    "member": "3884",
    "deposited": {
        "date-time": "2020-10-01T15:50:12Z",
    },
    "created": {
        "date-time": "2019-10-01T16:59:28Z",
    },
    "type": "journal-article",
    "references-count": 0,
    "is-referenced-by-count": 2,
}


class DatabaseTest(unittest.TestCase):

    def setUp(self):
        self.db = ClickHouseDB(database_name="testdb")
        self.db.recreate_table(table=CreativeWork, prompt=False)

    def test_create_table(self):
        self.db.create_table(table=CreativeWork)

    def test_insert_data(self):
        """
        Insert 2 rows into the 'creativework' table, each with member '3884'.
        """
        results_query = f"SELECT * FROM {CreativeWork.name_table()}"
        records = [
            CreativeWork.load_json(ITEM, has_refs=False),
            CreativeWork.load_json(ITEM, has_refs=False),
        ]
        self.db.insert_records(records=records)
        result = self.db.client.query(results_query)
        rows = [r for r in result.named_results()]
        expected = ["3884", "3884"]
        actual = [d.get("member") for d in rows]
        self.assertListEqual(expected, actual)


if __name__ == "__main__":
    unittest.main()
