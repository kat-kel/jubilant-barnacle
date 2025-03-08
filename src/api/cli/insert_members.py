from rich.progress import (
    BarColumn,
    MofNCompleteColumn,
    Progress,
    TextColumn,
    TimeElapsedColumn,
)
from src.api.client import Client
from src.api.database import ClickHouseDB
from src.api.models.member import CrossrefMember
from src.api.models.work import CreativeWork


class NotEnoughDataException(Exception):
    """There is not enough data in the 'creativeworks' table. \
        Make sure to run the commands in the correct order."""


def get_unique_members(db: ClickHouseDB) -> list[str]:
    """
    From the table of works, get a unique set of member IDs that have not yet \
        been entered into the members table.
    """

    works = CreativeWork.name_table()
    members = CrossrefMember.name_table()

    query = f"""
SELECT DISTINCT(w."member")
FROM {works} w
LEFT JOIN {members} m ON w.`member` = m.id
WHERE m.id  = ''
ORDER BY w."member"
"""
    result = db.client.query(query=query)
    return [row[0] for row in result.result_rows]


def insert_members():
    # Set up the client for calling the Crossref API
    client = Client()
    # Set up a connection to the ClickHouse database
    db = ClickHouseDB()
    # Affirm that the table for inserting values is created
    db.create_table(CrossrefMember)

    member_ids = get_unique_members(db=db)
    if len(member_ids) < 1:
        raise NotEnoughDataException

    # Set up a progress bar for tracking the API calls
    with Progress(
        TextColumn("{task.description}"),
        BarColumn(),
        MofNCompleteColumn(),
        TimeElapsedColumn(),
    ) as p:
        # Show the collection's parameters
        t = p.add_task("Collecting members", total=len(member_ids))

        # Run the multi-threaded API calls
        for record in client.get_members(ids=member_ids):
            # Insert the sample's data into the table
            db.insert_single_record(record=record)
            p.advance(t)
