# jubilant-barnacle

Exploration of the Crossref API and hypothesis about incoming citation counts relative to outgoing citations.

## I. Set up a local ClickHouse database

Download the open-source ClickHouse binary for a local installation.

```shell
curl https://clickhouse.com/ | sh
```

In a dedicated terminal, change to the directory of the downloaded binary files and start the ClickHouse database server.

```shell
./clickhouse server
```

Create an instance of the `Database` class from Infinidat's `inif.clickhouse_orm` (BSD-3 License) to connect to the default port, `http://localhost:8123`.

```python
from infi.clickhouse_orm import Database

db = Database("crossref")
```

## II. Model the pertinent data

1. Create a Python `dataclass` for each entity and a class method to parse the payload from the API's JSON response.

2. Create an `inif.clickhouse_orm` data model for each entity and its relevant properties.

## III. Call the API

1. Collect a sample of items from the API.

2. Iterate through each item in the sample.

3. Load the item into a Python dataclass, using the dataclass's class methods to parse the nested JSON metadata.

4. Load the key-word arguments from a dictionary representation of the dataclass instance into the `inif.clickhouse_orm` data model, using the `Database.insert()` method.

```python
# Using a custom class method, load the item into a datacalss
parsed_item = RecordDataclass.load_json(json_item)

# Load the data class's attributes into the ClickHouse model
item = ClickHouseModel(**parsed_item.__dict__)

# Insert the ClickHouse data model into the database
db.insert(item)
```
