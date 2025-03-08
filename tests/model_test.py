import unittest
from pathlib import Path

from src.api.models.work import CreativeWork

JSON = Path(__file__).parent.joinpath("works.json")

ITEM1 = {
    "DOI": "10.5840/ancientphil201434222",
    "member": "3884",
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
}

ITEM2 = {
    "DOI": "10.5840/ancientphil201434222",
    "member": "3884",
    "deposited": {
        "date-time": "2020-10-01T15:50:12Z",  # 3:50 PM
        # (later in the day than the creation)
    },
    "created": {
        "date-time": "2019-10-01T13:59:28Z",  # 1:59 PM
    },
    "type": "journal-article",
    "references-count": 0,
    "is-referenced-by-count": 2,
}


class ModelTest(unittest.TestCase):

    def test_dataclass_date_parsing_earlier(self):
        """
        The created datetime occurs earlier in the day than deposit datetime.
        This should make the difference between the dates equal to 365.
        """
        model = CreativeWork.load_json(item=ITEM1, has_refs=False)
        actual = model.deposit_delay_days
        expected = 365
        self.assertEqual(actual, expected)

    def test_dataclass_date_parsing_later(self):
        """
        The created datetime occurs later in the day than deposit datetime.
        This should add an extra day to the difference between the dates.
        """
        model = CreativeWork.load_json(item=ITEM2, has_refs=False)
        actual = model.deposit_delay_days
        expected = 366
        self.assertEqual(actual, expected)

    def test_class_string_attribute_conversion_to_sql(self):
        """
        The required and optional string attributes of the dataclass should \
            return a type of 'String' and 'Nullable(String)', respectively, \
            for the ClickHouse database.
        """
        attribute_type = CreativeWork.__annotations__["doi"]
        actual = CreativeWork.__column_type_name__(dtype=attribute_type)
        expected = "String"
        self.assertEqual(actual, expected)

        attribute_type = CreativeWork.__annotations__["member"]
        actual = CreativeWork.__column_type_name__(dtype=attribute_type)
        expected = "Nullable(String)"
        self.assertEqual(actual, expected)

    def test_class_int_attribute_conversion_to_sql(self):
        """
        The required and optional integer attributes of the dataclass should \
            return a type of 'Int64' and 'Nullable(Int64)', respectively, for \
            the ClickHouse database.
        """
        attribute_type = CreativeWork.__annotations__["citations_outgoing"]
        actual = CreativeWork.__column_type_name__(dtype=attribute_type)
        expected = "Int64"
        self.assertEqual(actual, expected)

        attribute_type = CreativeWork.__annotations__["citations_incoming"]
        actual = CreativeWork.__column_type_name__(dtype=attribute_type)
        expected = "Nullable(Int64)"
        self.assertEqual(actual, expected)


if __name__ == "__main__":
    unittest.main()
