import click

from src.api.cli.export_table import TABLE_CHOICES, export_table
from src.api.cli.insert_members import insert_members
from src.api.cli.insert_works import insert_works
from src.api.constants import CLICKHOUSE_DATABASE
from src.api.database import ClickHouseDB
from src.api.models.member import CrossrefMember
from src.api.models.work import CreativeWork


@click.group()
def cli():
    pass


@cli.command("drop-works")
def drop_works():
    db = ClickHouseDB()
    db.recreate_table(table=CreativeWork)


@cli.command("drop-members")
def drop_members():
    db = ClickHouseDB()
    db.recreate_table(table=CrossrefMember)


@cli.command("insert-members")
@click.option(
    "--database",
    type=click.STRING,
    default=CLICKHOUSE_DATABASE,
    show_default=True,
)
def members(database):
    insert_members(database_name=database)


@cli.command("insert-samples")
@click.option("--mailto", type=click.STRING)
@click.option("--samples", type=click.INT, required=True)
@click.option("--has-references", is_flag=True, default=False)
@click.option(
    "--database",
    type=click.STRING,
    default=CLICKHOUSE_DATABASE,
    show_default=True,
)
def works(mailto, samples, has_references, database):
    insert_works(
        mailto=mailto,
        samples=samples,
        has_references=has_references,
        database=database,
    )


@cli.command("export-parquet")
@click.option("--table", required=True, type=click.Choice(TABLE_CHOICES))
@click.option(
    "--outfile",
    type=click.Path(file_okay=True, dir_okay=False),
    required=True,
)
def export(table: str, outfile: str):
    export_table(table_choice=table, outfile=outfile)


if __name__ == "__main__":
    cli()
