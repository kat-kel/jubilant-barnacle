import click
from rich.console import Console
from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

from src.api.client import Client
from src.api.database import ClickHouseDB
from src.api.models.work import CreativeWork


@click.group()
def cli():
    pass


@cli.command("drop-works")
def drop():
    # Set up a connection to the ClickHouse database
    db = ClickHouseDB()
    db.recreate_table(table=CreativeWork)


class ConsoleLog:
    """Cosmetic helper for remembering the ongoing collection's parameters."""

    def __init__(self, db: ClickHouseDB, refs: bool) -> None:
        self.db = db.database_name
        self.refs = refs
        self.table = CreativeWork.name_table()
        self.console = Console()
        self.console.clear()

    def print_log(self) -> None:
        self.console.print(f"\tConnected to database '{self.db}'")
        self.console.print(f"\tInserting values into table '{self.table}'")
        self.console.print(f"\tHas references: {self.refs}")

    def refresh(self) -> None:
        self.console.clear()
        self.print_log()


@cli.command("insert-samples")
@click.option("--mailto", type=click.STRING)
@click.option("--samples", type=click.INT)
@click.option("--has-references", is_flag=True, default=False)
def collect(mailto, samples, has_references):
    # Set up the client for calling the Crossref API
    client = Client(mailto=mailto)
    # Set up a connection to the ClickHouse database
    db = ClickHouseDB()
    # Set up a stdout log for the console
    console = ConsoleLog(db=db, refs=has_references)
    # Affirm that the table for inserting values is created
    db.create_table(CreativeWork)

    # Set up a progress bar for tracking the API calls
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
        console=console.console,
    ) as p:
        # Show the collection's parameters
        console.print_log()
        t = p.add_task("Collecting samples", total=samples)

        # Run the multi-threaded API calls
        for response in client.get_samples(
            has_references=has_references,
            n=samples,
        ):
            # Refresh the stdout log
            console.refresh()
            # Parse the API response
            items = response["message"]["items"]
            records = [CreativeWork.load_json(i) for i in items]
            # Insert the sample's data into the table
            db.insert_records(records=records)
            p.advance(t)


if __name__ == "__main__":
    cli()
