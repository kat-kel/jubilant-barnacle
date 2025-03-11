from dataclasses import dataclass
from pathlib import Path

import pyarrow as pa
import pyarrow.parquet as pq

from src.api.database import ClickHouseDB
from src.api.models.base import BaseModel
from src.api.models.member import CrossrefMember
from src.api.models.work import CreativeWork


@dataclass
class Works:
    choice: str = "works"
    table: BaseModel = CreativeWork


@dataclass
class Members:
    choice: str = "members"
    table: BaseException = CrossrefMember


TABLE_CHOICES = [Works.choice, Members.choice]


def make_sure_outfile_is_parquet(outfile: str) -> Path:
    """
    Affirm that the outfile path has the suffix ".parquet".

    Args:
        outfile (str): File path for the parquet export.

    Raises:
        ValueError: If the file path is invalid, pathlib will raise an error.

    Returns:
        Path: Valid path to the outfile.
    """

    fp = Path(outfile)
    [p.mkdir(exist_ok=True) for p in fp.parents]
    return fp.with_suffix(".parquet")


def build_query_for_selecting_distinct_rows(table: BaseModel) -> str:
    """
    Compose the select part of a query that ignores a table's duplicates rows.
    Because ClickHouse stores and represents dates in Unix, convert hem to a \
        date format.

    Args:
        table (BaseModel): Dataclass storing metadata about a table.

    Returns:
        str: SQL select query.
    """

    # Patch for handling ClickHouse's date representations in Unix.
    date_cols = [
        c
        for c, t in zip(
            table.__annotations__.keys(),
            table.list_column_type_names(),
        )
        if t == "DateTime"
    ]

    def reformat(col_name: str) -> str:
        if col_name in date_cols:
            return f"formatDateTime({col_name}, '%Y-%m-%d') AS {col_name}"
        return col_name

    column_names = ", ".join(
        [f"{reformat(k)}" for k in table.__annotations__.keys()],
    )
    columns = ", ".join(table.__annotations__.keys())
    table_name = table.name_table()
    query = f"SELECT DISTINCT ON ({columns}) {column_names} FROM {table_name}"
    return query


def fetch_unique_rows_in_pyarrow(
    table: BaseModel,
    db: ClickHouseDB,
) -> pa.Table:
    """
    Select the unique rows from a table and return them in a Pyarrow table.

    Args:
        table (BaseModel): Dataclass storing metadata about a table.
        db (ClickHouseDB): ClickHouse database class instance.

    Returns:
        Table: Pyarrow table.
    """

    selection_query = build_query_for_selecting_distinct_rows(table=table)
    return db.client.query_arrow(query=selection_query)


def write_pyarrow_table_to_parquet(pyarrow_table: pa.Table, fp: Path) -> None:
    pq.write_table(pyarrow_table, fp)


def export_table(table_choice: str, outfile: str, database: str):
    if table_choice == Works.choice:
        table = Works.table
    elif table_choice == Members.choice:
        table = Members.table
    else:
        raise ValueError("This table is not yet implemented")

    fp = make_sure_outfile_is_parquet(outfile=outfile)
    db = ClickHouseDB(database_name=database)
    selection = fetch_unique_rows_in_pyarrow(table=table, db=db)
    write_pyarrow_table_to_parquet(pyarrow_table=selection, fp=fp)
