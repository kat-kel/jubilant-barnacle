import click
import duckdb
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from src.analysis.constants import WORKS_TABLE  # , MEMBERS_TABLE
from src.analysis.utils import select_parquet_columns


def load_parquet_table(
    infile: str,
    table_name: str,
    conn: duckdb.DuckDBPyConnection,
) -> None:
    console = Console()

    with Progress(
        TextColumn("{task.description}"),
        SpinnerColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as p:
        _ = p.add_task(f"(Re)creating table '{table_name}'")
        conn.execute(f"DROP TABLE IF EXISTS {table_name}")
        selection = select_parquet_columns(table_name=table_name)
        create_stmt = f"""
CREATE TABLE {table_name} AS SELECT {selection} FROM read_parquet('{infile}')
"""
        conn.execute(create_stmt)
        console.print(f"Preview of table '{table_name}'", style="red")
        print(conn.table(table_name).limit(2))


@click.command()
@click.option(
    "--members",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
)
@click.option(
    "--works",
    type=click.Path(exists=True, file_okay=True, dir_okay=False),
    required=True,
)
@click.option("--database", required=True)
def main(members: str, works: str, database: str):
    conn = duckdb.connect(database=database)

    load_parquet_table(infile=works, table_name=WORKS_TABLE, conn=conn)
    # load_parquet_table(infile=members, table_name=MEMBERS_TABLE, conn=conn)


if __name__ == "__main__":
    main()
