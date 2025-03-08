# jubilant-barnacle

Exploration of the Crossref API and hypothesis about incoming citation counts relative to outgoing citations.

- [Collect data](#collect-data)

  1. [Set up local ClickHouse database](#1-set-up-a-local-clickhouse-database)
  2. [Install this project's Python CLI](#2-install-this-projects-python-cli)
  3. [Insert works into ClickHouse](#3-insert-samples-into-clickhouse)
  4. [Insert works' members into ClickHouse](#4-insert-members-into-clickhouse)
  5. [Backup data / export tables](#5-backup-the-collected-data)

- [Analyse data](#analyse-data)

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

```shell
crossref-api insert-members --matilto "my.email@mail.com"
```

### 5. Backup the collected data

The data inserted into the ClickHouse database is stored in a folder where the software was installed. Specifically, ClickHouse local creates a symbolic link from a table's directory in `data/` to binary files in the `store/`.

```shell
clickhouse/data/crossref/creativework/ -> clickhouse/store/8ca/8cac4d5e-620a-4ee0-9dc3-6199fdefc23f
```

In case we uninstall / delete the ClickHouse local software, and thus delete the `data/` and `/store` folders, we need to back up our data in an open-source file format, such as parquet.

Run the export command for each table, specifying the name and location of the parquet file with which you want to work.

```shell
crossref-api export-parquet --table creativework --outfile ./sampled-data/works.parquet
```

```shell
crossref-api export-parquet --table member --outfile ./sampled-data/members.parquet
```

## Analyse data
