import datetime
import typing
from dataclasses import dataclass

from src import LOG_DIR

from .base import BaseModel


@dataclass
class CreativeWork(BaseModel):
    doi: str
    deposited: datetime.datetime
    created: datetime.datetime
    deposit_delay_days: int
    has_refs: bool
    citations_incoming: typing.Optional[int] = None
    citations_outgoing: int = 0
    member: typing.Optional[str] = None
    work_type: typing.Optional[str] = None

    @classmethod
    def parse_date(cls, obj: dict) -> datetime:
        s = obj["date-time"]
        return datetime.datetime.fromisoformat(s)

    @classmethod
    def load_json(cls, item: dict) -> "CreativeWork":
        try:
            doi = item["DOI"]
            work_type = item.get("type")
            created = cls.parse_date(item["created"])
            citations_incoming = item.get("is-referenced-by-count")
            member = item.get("member")
            deposited = cls.parse_date(item["deposited"])
            citations_outgoing = item.get("references-count")
            if citations_outgoing:
                has_refs = True
            else:
                has_refs = False
            deposit_delay_days = (deposited - created).days

        # If the parsing fails, log the invalid data and abort the process.
        except Exception as e:
            import json

            with open(LOG_DIR.joinpath("error.txt"), "w") as f:
                f.write(str(e))
            with open(LOG_DIR.joinpath("invalid_item.json"), "w") as f:
                json.dump(item, f, indent=4)
            raise e

        return CreativeWork(
            doi=doi,
            member=member,
            deposited=deposited,
            created=created,
            deposit_delay_days=deposit_delay_days,
            citations_outgoing=citations_outgoing or 0,
            citations_incoming=citations_incoming,
            has_refs=has_refs,
            work_type=work_type,
        )
