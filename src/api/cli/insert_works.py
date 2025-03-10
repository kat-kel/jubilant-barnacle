from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)

from src.api.cli.console import ConsoleLog
from src.api.constants import CLICKHOUSE_DATABASE
from src.api.client import Client
from src.api.database import ClickHouseDB
from src.api.models.work import CreativeWork


def insert_works(
    mailto: str | None,
    samples: int,
    has_references: bool,
    database: str = CLICKHOUSE_DATABASE,
):
    # Set up the client for calling the Crossref API
    client = Client(mailto=mailto)
    # Set up a connection to the ClickHouse database
    db = ClickHouseDB(database_name=database)
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
        for records in client.get_samples(
            has_references=has_references,
            n=samples,
        ):
            # Refresh the stdout log
            console.refresh()
            # Insert the sample's data into the table
            db.insert_records(records=records)
            p.advance(t)
