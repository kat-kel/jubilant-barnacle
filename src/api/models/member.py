import datetime
import statistics
import typing
from dataclasses import dataclass

from src.api.cli.logs import LOG_DIR

from .base import BaseModel

INVALID_ITEM = LOG_DIR.joinpath("invalid_item.json")


@dataclass
class CrossrefMember(BaseModel):
    id: int  # id
    name: str  # primary-name
    total_dois: int  # counts.total-dois
    creation_pvariance: float
    creation_mean: int

    # breakdowns.dois-by-issued-year[-1]
    creation_earliest: int

    # breakdowns.dois-by-issued-year[0]
    creation_latest: int

    # coverage.references-current
    references_current: float

    # counts-type.all.journal-article
    journal_articles: typing.Optional[int] = 0

    # counts-type.all.book-chapter
    book_chapters: typing.Optional[int] = 0

    # counts-type.all.proceedings-article
    proceedings_articles: typing.Optional[int] = 0

    @classmethod
    def load_json(cls, message: dict) -> "CrossrefMember":

        try:
            id = message["id"]
            name = message["primary-name"]
            total_dois = message["counts"]["total-dois"]

            year_counts = message["breakdowns"]["dois-by-issued-year"]
            earliest_creation = year_counts[-1][0]
            latest_creation = year_counts[0][0]

            years = []
            for y, c in year_counts:
                years.extend([y] * c)
            creation_year_mean = int(
                round(statistics.geometric_mean(years), 0),
            )
            creation_year_pvariance = statistics.pvariance(years)

            count_types = message["counts-type"]["all"]
            journal_articles = count_types.get("journal-article")
            book_chapters = count_types.get("book-chapter")
            proceedings_articles = count_types.get("proceedings-article")

            references_current = message["coverage"]["references-current"]

        except KeyError as e:
            import json

            with open(INVALID_ITEM, "w") as f:
                obj = {
                    "key-error": e.args,
                    "time": str(datetime.datetime.now()),
                    "item": message,
                }
                json.dump(obj, f, indent=4)
            raise e

        return CrossrefMember(
            id=id,
            name=name,
            total_dois=total_dois,
            creation_mean=creation_year_mean,
            creation_pvariance=creation_year_pvariance,
            creation_earliest=earliest_creation,
            creation_latest=latest_creation,
            journal_articles=journal_articles or 0,
            book_chapters=book_chapters or 0,
            proceedings_articles=proceedings_articles or 0,
            references_current=references_current,
        )
