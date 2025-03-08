from src.analysis.constants import MEMBERS_TABLE, WORKS_TABLE
from src.api.models.base import BaseModel
from src.api.models.member import CrossrefMember
from src.api.models.work import CreativeWork


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


def recast_columns(model: BaseModel) -> str:
    cols = []
    date_cols = list_date_cols(model=model)
    for k in model.__annotations__.keys():
        if k in date_cols:
            cols.append(f"""strptime({k}, '%Y-%m-%d') AS {k}""")
        else:
            cols.append(k)
    return ", ".join(cols)


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
        return recast_columns(model=CreativeWork)
    elif table_name == MEMBERS_TABLE:
        return recast_columns(model=CrossrefMember)
    else:
        raise ValueError("Invalid table name")
