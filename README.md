# jubilant-barnacle

Exploration of the Crossref API and hypothesis about incoming citation counts relative to outgoing citations.

- [Collect data](#collect-data)

  1. [Set up local ClickHouse database](#1-set-up-a-local-clickhouse-database)
  2. [Install this project's Python CLI](#2-install-this-projects-python-cli)
  3. [Insert works into ClickHouse](#3-insert-samples-into-clickhouse)
  4. [Insert works' members into ClickHouse](#4-insert-members-into-clickhouse)
  5. [Backup data / export tables](#5-backup-the-collected-data)

- [Analyse data](#analyse-data)
  
  1. [Install Python dependencies](#1-install-notebook-dependencies)
  2. [Load backups into DuckDB](#2-load-the-backed-up-data-into-duckdb)
  3. [Launch Jupyter notebook](#3-develop-analyses-in-notebook)

Credits to open-source projects used in this workflow:

|author|project|use in workflow|license|
|--|--|--|--|
|ClickHouse|[local database](https://clickhouse.com/docs/operations/utilities/clickhouse-local) & [`clickhouse-connect`](https://clickhouse.com/docs/integrations/python) Python API|distributed database|Apache-2.0 License|
|Apache Arrow|[`pyarrow`](https://arrow.apache.org/docs/python/index.html) Python API|data backup|Apache-2.0 License|
|DuckDB|[`duckdb`](https://duckdb.org/docs/stable/clients/python/overview) Python API|OLAP database|MIT License|
|Sciences Po, _médialab_|[`minet`](https://github.com/medialab/minet) Python library|multi-threaded API requests|GPL-3.0 License|
|Textualize & Will McGugan|[`rich`](https://github.com/Textualize/rich) Python library|CLI progress bar|MIT License|
|Paletts|[`click`](https://github.com/pallets/click) Python library|CLI commands|BSD-3-Clause License|
|Michael Waskom|[`seaborn`](https://github.com/mwaskom/seaborn) Python library| data visualisation|BSD-3-Clause License|

---

## Collect data

### 1. Set up a local ClickHouse database

Download the open-source ClickHouse binary for a local installation.

```shell
curl https://clickhouse.com/ | sh
```

In a dedicated terminal, change to the directory of the downloaded binary files and start the ClickHouse database server.

```shell
./clickhouse server
```

### 2. Install this project's Python CLI

1. Download this repository with `git clone git@github.com:kat-kel/jubilant-barnacle.git`.

2. Change to the project directory, `cd jubilant-barnacle`.

3. Create a new virtual Python environment, version 3.12, named something like `crossref-api`.

4. Activate the `crossref-api` virtual Python environment.

5. From the root of the project's directory, run `pip install .` to install the data collection CLI.

### 3. Insert samples into ClickHouse

Start collecting samples of creative works from the Crossref API with the command `crossref-api insert-samples`.

```shell
crossref-api insert-samples --samples 100 --mailtto "my.email@mail.com"
```

By default, the command will apply a filter to collect only works without references. If/when you want to collect works with references, add the option `--has-references`.

```shell
crossref-api insert-samples --samples 100 --mailto "my.email@mail.com" --has-references
```

Once you run the command, the console will clear and it will monitor the script's progress as it collects the number of samples you ordered with the `--samples` parameter, i.e. 100 samples.

```console
        Connected to database 'crossref'
        Inserting values into table 'creativework'
        Has references: True
Collecting samples ━━━━━━━━━━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━  32/100 0:02:38
```

### 4. Insert members into ClickHouse

After the samples have been collected, run the command to collect metadata about the members that are included in the samples.

```console
$ crossref-api insert-members
Collecting members ━━━━━━━━━╺━━━  750/1000 0:17:43
```

### 5. Backup the collected data

The data inserted into the ClickHouse database is stored in a folder where the software was installed. Specifically, ClickHouse local creates a symbolic link from a table's directory in `data/` to binary files in the `store/`.

In case we uninstall / delete the ClickHouse local software, and thus delete the `data/` and `/store` folders, we need to back up our data.

Run the export command for each table, specifying the name and location of the parquet file with which you want to work during the data analysis.

```shell
crossref-api export-parquet --table works --outfile ./sampled-data/works.parquet
```

```shell
crossref-api export-parquet --table members --outfile ./sampled-data/members.parquet
```

## Analyse data

### 1. Install notebook dependencies

Install the dependencies used for data analysis, namely `jupyterlab` and `seaborn`.

```shell
pip install ".[jup]"
```

### 2. Load the backed up data into DuckDB

Load the backups of the collected data into a DuckDB database file.

```console
$ crossref-duck --members sampled-data/members.parquet --works sampled-data/works.parquet --database sampled-data/crossref.duckdb
─────────────────────────────────── Table 'works' ───────────────────────────────────
Rows: 1978118
┌──────────────────────┬─────────────────────┬───┬─────────┬─────────────────┐
│         doi          │      deposited      │ … │ member  │    work_type    │
│       varchar        │      timestamp      │   │ varchar │     varchar     │
├──────────────────────┼─────────────────────┼───┼─────────┼─────────────────┤
│ 10.1002/ece3.70502   │ 2025-02-18 00:00:00 │ … │ 311     │ journal-article │
│ 10.3389/fpsyt.2021…  │ 2024-09-19 00:00:00 │ … │ 1965    │ journal-article │
├──────────────────────┴─────────────────────┴───┴─────────┴─────────────────┤
│ 2 rows                                                 9 columns (4 shown) │
└────────────────────────────────────────────────────────────────────────────┘

Creating table ⠸ 0:00:01
────────────────────────────────── Table 'members' ──────────────────────────────────
Rows: 18778
┌─────────┬──────────────────────┬───┬───────────────┬──────────────────────┐
│   id    │         name         │ … │ book_chapters │ proceedings_articles │
│ varchar │       varchar        │   │     int64     │        int64         │
├─────────┼──────────────────────┼───┼───────────────┼──────────────────────┤
│ 9052    │ Institute for Soci…  │ … │             0 │                    0 │
│ 9523    │ International Asso…  │ … │             0 │                 4477 │
├─────────┴──────────────────────┴───┴───────────────┴──────────────────────┤
│ 2 rows                                               11 columns (4 shown) │
└───────────────────────────────────────────────────────────────────────────┘

Creating table ⠋ 0:00:00
```

### 3. Develop analyses in notebook

Launch `jupyter-lab` and begin analysing the sampled works and members data in the [notebook](./notebook.ipynb).
