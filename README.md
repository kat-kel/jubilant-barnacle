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

## II. Insert samples into ClickHouse

1. Create and activate a virtual Python environment, version 3.12.

2. Download this repository with `git clone git@github.com:kat-kel/jubilant-barnacle.git`. Then change to the directory, `cd jubilant-barnacle`.

3. From the root of the project's directory, install the Python package with `pip install .`.

4. Run a collection from the Crossref API with the `crossref-api insert-samples` command.

```shell
crossref-api insert-samples --samples 100 --mailtto "my.email@mail.com"
```

By default, the command will apply a filter to collect only works without references. If/when you want to collect works with references, add the option `--has-references`.

Once you run the command, the console will clear and it will monitor your progress through the amount of samples you wanted.

```console
        Connected to database 'crossref'
        Inserting values into table 'creativework'
        Has references: True
Collecting samples ━━━━━━━━━━━━╸━━━━━━━━━━━━━━━━━━━━━━━━━━━  32/100 0:02:38
```
