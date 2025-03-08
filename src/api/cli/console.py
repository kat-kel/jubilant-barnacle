from rich.console import Console

from src.api.database import ClickHouseDB
from src.api.models.work import CreativeWork


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
