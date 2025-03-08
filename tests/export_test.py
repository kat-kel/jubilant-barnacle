import unittest
from pathlib import Path
import pyarrow.parquet as pq

from src.api.cli.export_table import (
    build_query_for_selecting_distinct_rows,
    make_sure_outfile_is_parquet,
    fetch_unique_rows_in_pyarrow,
    write_pyarrow_table_to_parquet,
)
from src.api.database import ClickHouseDB
from src.api.models.work import CreativeWork

ITEMS = [
    {
        "DOI": "10.1123/att.5.5.39",
        "member": "100",
        "deposited": {
            "date-time": "2020-10-01T15:50:12Z",  # 3:50 PM
            # (earlier in the day than the creation)
        },
        "created": {
            "date-time": "2019-10-01T16:59:28Z",  # 4:59 PM
        },
        "type": "journal-article",
        "references-count": 0,
        "is-referenced-by-count": 2,
    },
    {
        "DOI": "10.1123/att.5.5.39",
        "member": "100",
        "deposited": {
            "date-time": "2020-10-01T15:50:12Z",  # 3:50 PM
            # (earlier in the day than the creation)
        },
        "created": {
            "date-time": "2019-10-01T16:59:28Z",  # 4:59 PM
        },
        "type": "journal-article",
        "references-count": 0,
        "is-referenced-by-count": 2,
    },
    {
        "DOI": "10.1021/ac00002a012",
        "member": "316",
        "deposited": {
            "date-time": "2020-10-01T15:50:12Z",  # 3:50 PM
            # (earlier in the day than the creation)
        },
        "created": {
            "date-time": "2019-10-01T16:59:28Z",  # 4:59 PM
        },
        "type": "journal-article",
        "references-count": 0,
        "is-referenced-by-count": 2,
    },
]


class DatabaseTest(unittest.TestCase):
    def setUp(self):
        """
        Create a 'creativeworks' table with 3 rows, 2 of which are duplicates.
        """
        db = ClickHouseDB(database_name="testdb")
        db.recreate_table(table=CreativeWork, prompt=False)
        db.insert_records(
            [CreativeWork.load_json(item=i, has_refs=False) for i in ITEMS]
        )
        self.dbclient = db.client
        self.db = db
        self.outfile = Path(__file__).parent.joinpath("works.parquet")

    def test_sql_query(self):
        """
        The query should return 2 rows from the table, ignoring one of the \
            duplicates.
        """
        query = build_query_for_selecting_distinct_rows(table=CreativeWork)
        result = self.dbclient.query(query)
        actual = result.row_count
        expected = 2
        self.assertEqual(actual, expected)

    def test_fetch_pyarrow_table(self):
        """
        The function should generate a Pyarrow table with 2 rows, ignoring 1 \
            of the duplicates.
        """
        result = fetch_unique_rows_in_pyarrow(table=CreativeWork, db=self.db)
        actual = result.num_rows
        expected = 2
        self.assertEqual(actual, expected)

    def test_write_parquet(self):
        """
        The test will generate a Pyarrow table with 2 rows ignoring 1 of the \
            duplicates, then write that Pyarrow table to a parquet file. The \
            written file should be valid, capable of being parsed with \
            Pyarrow's reader, and contain the same tabular data as what was \
            used to write it.
        """
        input_pyarrow_table = fetch_unique_rows_in_pyarrow(
            table=CreativeWork,
            db=self.db,
        )
        input = input_pyarrow_table.to_pydict()
        write_pyarrow_table_to_parquet(
            pyarrow_table=input_pyarrow_table,
            fp=self.outfile,
        )
        output_parquet_table = pq.ParquetFile(self.outfile).read()
        output = output_parquet_table.to_pydict()
        self.assertDictEqual(input, output)

    def tearDown(self):
        if self.outfile.is_file():
            self.outfile.unlink()


class OutfilePathTest(unittest.TestCase):
    expected = Path("works.parquet")

    def test_parquet_suffix(self):
        """
        When a user enters 'works.parquet', the function should return the \
            same path.
        """
        user_param = "works.parquet"
        actual = make_sure_outfile_is_parquet(outfile=user_param)
        self.assertEqual(actual, self.expected)

    def test_csv_suffix(self):
        """
        When a user enters 'works.csv', the function should keep the stem and \
            modify the file ending, returning 'works.parquet'.
        """
        user_param = "works.csv"
        actual = make_sure_outfile_is_parquet(outfile=user_param)
        self.assertEqual(actual, self.expected)

    def test_no_suffix(self):
        """
        When a user enters 'works', without a file ending, the function \
            should keep the stem and add a file ending, returning \
            'works.parquet'.
        """
        user_param = "works"
        actual = make_sure_outfile_is_parquet(outfile=user_param)
        self.assertEqual(actual, self.expected)


if __name__ == "__main__":
    unittest.main()
