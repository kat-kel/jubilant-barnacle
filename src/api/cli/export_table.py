from pathlib import Path
from typing import Literal

from src.api.database import ClickHouseDB
from src.api.models.work import CreativeWork

TABLE_CHOICES = Literal["work", "member"]


def make_sure_outfile_is_parquet(outfile: str) -> Path:
    fp = Path(outfile)
    return fp.with_suffix(".parquet")


def export_table(table: TABLE_CHOICES, outfile: str):
    fp = make_sure_outfile_is_parquet(outfile=outfile)
    db = ClickHouseDB()
    if table == "work":
        table_name = CreativeWork.name_table()
    else:
        raise ValueError("This table is not yet implemented")

    export_query = f"""
SELECT * FROM {table_name} INTO OUTFILE {fp}
"""
    db.client.command(export_query)
