import click
import duckdb
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    TimeElapsedColumn,
)

from src.analysis.constants import WORKS_TABLE
from src.analysis.utils import select_parquet_columns


def load_table(
    infile: str,
    table: str,
    conn: duckdb.DuckDBPyConnection,
) -> None:
    console = Console()

    with Progress(
        TextColumn("{task.description}"),
        SpinnerColumn(),
        TimeElapsedColumn(),
        console=console,
    ) as p:
        _ = p.add_task("(Re)creating works table")
        conn.execute(f"DROP TABLE IF EXISTS {table}")
        selection = select_parquet_columns(table_name=WORKS_TABLE)
        create_stmt = f"""
CREATE TABLE {table} AS SELECT {selection} FROM read_parquet('{infile}')"""
        conn.execute(create_stmt)
        console.print(f"Preview of table '{table}'", style="red")
        print(conn.table(table).limit(2))


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

    load_table(infile=works, table=WORKS_TABLE, conn=conn)
    # load_table(infile=members, table=MEMBERS_TABLE, conn=conn)


if __name__ == "__main__":
    main()
