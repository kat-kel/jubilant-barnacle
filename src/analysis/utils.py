from src.analysis.constants import WORKS_TABLE
from src.api.models.base import BaseModel
from src.api.models.work import CreativeWork

# from src.api.models.member import CrossrefMember


def list_date_cols(model: BaseModel) -> list[str]:
    """
    List all the columns in the table that represent dates.

    Args:
        model (BaseModel): Data model for the table.

    Returns:
        list[str]: Names of columns for date data.
    """

    return [
        c
        for c, t in zip(
            model.__annotations__.keys(),
            model.list_column_type_names(),
        )
        if t == "DateTime"
    ]


def select_parquet_columns(table_name: str) -> str:
    """
    Select and, when a date, recast the columns of the parquet file for \
        inserting into a DuckDB database table.

    Args:
        table_name (str): Name of a table to be created in the DuckDB database.

    Returns:
        str: Column portion of the query for selecting the parquet data.
    """
    if table_name == WORKS_TABLE:
        cols = []
        date_cols = list_date_cols(model=CreativeWork)
        for k in CreativeWork.__annotations__.keys():
            if k in date_cols:
                cols.append(f"""strptime({k}, '%Y-%m-%d')""")
            else:
                cols.append(k)
        return ", ".join(cols)
    else:
        raise ValueError("Invalid table name")
