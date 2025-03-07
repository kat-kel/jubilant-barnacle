import typing
from datetime import datetime


class BaseModel:
    suffix = "Engine MergeTree ORDER BY tuple()"

    def serialize(self) -> dict:
        j = {}
        for k, v in self.__dict__.items():
            if isinstance(v, datetime):
                v = str(v)
            j.update({k: v})
        return j

    @classmethod
    def name_table(cls) -> str:
        return cls.__name__.lower()

    @staticmethod
    def __column_type_name__(dtype: typing.Any) -> str:
        """
        Convert the type annotation of the class's attribute to a ClickHouse
        data type.
        """
        if str(dtype) == "<class 'datetime.datetime'>" in str(dtype):
            return "DateTime"
        elif str(dtype) == "<class 'int'>":
            return "Int64"
        elif str(dtype) == "typing.Optional[int]":
            return "Nullable(Int64)"
        elif str(dtype) == "<class 'bool'>":
            return "Boolean"
        elif str(dtype) == "<class 'str'>":
            return "String"
        else:
            return "Nullable(String)"

    @classmethod
    def create_drop_statement(cls) -> str:
        return f"DROP TABLE IF EXISTS {cls.name_table()}"

    @classmethod
    def create_table_statement(cls) -> str:
        attrs = cls.__annotations__.items()
        cols = {n: cls.__column_type_name__(dtype) for n, dtype in attrs}
        c_string = ", ".join(f"{col} {dtype}" for col, dtype in cols.items())
        return f"""
CREATE TABLE IF NOT EXISTS {cls.name_table()}
({c_string})
{cls.suffix}
"""

    @classmethod
    def list_column_type_names(cls) -> list[str]:
        attrs = cls.__annotations__.items()
        return [cls.__column_type_name__(t) for _, t in attrs]
