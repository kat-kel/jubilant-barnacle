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
