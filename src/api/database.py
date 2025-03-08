import click
import clickhouse_connect
from datetime import datetime

from src.api.cli.logs import LOG_DIR
from src.api.models.base import BaseModel

INVALID_RECORDS = LOG_DIR.joinpath("invalid_records_chunk.json")


class ClickHouseDB:
    host = "localhost"
    port = 8123

    def __init__(self, database_name: str = "crossref") -> None:
        """
        Create an instance of the clickhouse-connect client. If the database \
            is not already created, create the database.

        Args:
            database_name (str): Name of the database in the ClickHouse \
                server instance. Defaults to 'crossref'.
        """
        # Ensure the database is created
        self.database_name = database_name
        self.client = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
        )
        db_create_stmt = f"""
CREATE DATABASE IF NOT EXISTS {database_name}
"""
        self.client.command(db_create_stmt)

        # Re-establish the connection and set the client to the database
        self.client.close()
        self.client = clickhouse_connect.get_client(
            host=self.host,
            port=self.port,
            database=database_name,
        )

    def insert_single_record(self, record: BaseModel) -> None:
        """
        Insert 1 modelled data record into the relevant ClickHouse DB table. \
            The data needs to be modelled according to a dataclass that \
            inherits from my BaseModel class, which features methods to \
            prepare the data for insertion into the databaes table.

        Args:
            records (BaseModel): An instance of a record's dataclass.
        """

        table = record.name_table()
        data = [list(record.__dict__.values())]
        column_names = list(record.__dict__.keys())
        column_type_names = record.list_column_type_names()
        try:
            self.client.insert(
                table=table,
                data=data,
                database=self.database_name,
                column_names=column_names,
                column_type_names=column_type_names,
            )

        # If the SQL command fails, log the invalid records and
        # abort the process.
        except Exception as e:
            import json

            with open(INVALID_RECORDS, "w") as f:
                obj = {
                    "error": str(e),
                    "time": str(datetime.now()),
                    "items": record.serialize(),
                }
                json.dump(obj, f, indent=4)
            raise e

    def insert_records(self, records: list[BaseModel]) -> None:
        """
        Insert a list of modelled data into the relevant ClickHouse DB table. \
            The data needs to be modelled according to a dataclass that \
            inherits from my BaseModel class, which features methods to \
            prepare the data for insertion into the databaes table.

        Args:
            records (list[BaseModel]): An instance of a record's dataclass.
        """

        model = records[0]
        table = model.name_table()
        data = [list(r.__dict__.values()) for r in records]
        column_names = list(model.__dict__.keys())
        column_type_names = model.list_column_type_names()
        try:
            self.client.insert(
                table=table,
                data=data,
                database=self.database_name,
                column_names=column_names,
                column_type_names=column_type_names,
            )

        # If the SQL command fails, log the invalid records and
        # abort the process.
        except Exception as e:
            import json

            with open(INVALID_RECORDS, "w") as f:
                obj = {
                    "error": str(e),
                    "time": str(datetime.now()),
                    "items": [r.serialize() for r in records],
                }
                json.dump(obj, f, indent=4)
            raise e

    def recreate_table(self, table: BaseModel, prompt: bool = True) -> None:
        """
        Drop a table if it exists, then create it anew, losing all data. \
            Unless prompt = False, make the user confirm they want to drop \
            the table.

        Args:
            table (BaseModel): Dataclass that inherits from the BaseModel and \
                represents a ClickHouse database table.
            prompt (bool, optional): Whether to prompt the user before \
                dropping a table. Defaults to True.
        """

        q = f"Do you want to drop all the data in table \
'{table.name_table()}' in database '{self.database_name}'?"
        if not prompt or click.prompt(q):
            stmt = table.create_drop_statement()
            self.client.command(stmt)
            self.create_table(table=table)

    def create_table(self, table: BaseModel) -> str:
        """
        Create a table in the ClickHouse database to which the client is \
            connected.

        Args:
            table (BaseModel): Dataclass that inherits from the BaseModel and \
                represents a ClickHouse database table.

        Returns:
            str: Description of the created table's columns.
        """

        table_name = table.name_table()
        stmt = table.create_table_statement()
        self.client.command(stmt)
        result = self.client.query(f"DESCRIBE TABLE {table_name}")
        return [r[0:2] for r in result.result_rows]
