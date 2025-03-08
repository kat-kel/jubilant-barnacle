import datetime
import typing
from dataclasses import dataclass

from src.api.cli.logs import LOG_DIR

from .base import BaseModel

# Set up logs for a work's validation
INVALID_ITEM = LOG_DIR.joinpath("invalid_item.json")


@dataclass
class CreativeWork(BaseModel):
    doi: str
    deposited: datetime.datetime
    created: datetime.datetime
    deposit_delay_days: int

    # This boolean needs to be provided alongside the item metadata because (to
    # optimise API) references array is not selected and whether an item has an
    # array of references is known only via the API call's filter parameter.
    has_refs: bool

    # Default to None because this metadata is unknown to Crossref
    citations_incoming: typing.Optional[int] = None

    # Default to 0 because this metadata is known to Crossref
    citations_outgoing: int = 0

    member: typing.Optional[str] = None
    work_type: typing.Optional[str] = None

    @classmethod
    def parse_date(cls, obj: dict) -> datetime:
        s = obj["date-time"]
        return datetime.datetime.fromisoformat(s)

    @classmethod
    def load_json(cls, item: dict, has_refs: bool) -> "CreativeWork":
        """
        From the JSON response returned by the API, parse a work's metadata. \
            To optimise the API call, the work's references array is not \
            returned and whether it has an array of references is known only \
            via the API call's filter parameter, so that metadata needs to be \
            provided separately.

            Args:
                item (dict): JSON object of work's selected metadata.
                has_refs (bool): Boolean used in API filter parameter.

            Raises:
                e: Key Error raised if metadata's formatting is invalid \
                    according to the data model.

            Returns:
                CreativeWork: An instance of the CreativeWork dataclass model.
        """

        try:
            doi = item["DOI"]
            work_type = item.get("type")
            created = cls.parse_date(item["created"])
            citations_incoming = item.get("is-referenced-by-count")
            member = item.get("member")
            deposited = cls.parse_date(item["deposited"])
            citations_outgoing = item.get("references-count")
            deposit_delay_days = (deposited - created).days

        # If the parsing fails, log the invalid data and abort the process.
        except KeyError as e:
            import json

            with open(INVALID_ITEM, "w") as f:
                obj = {
                    "key-error": e.args,
                    "time": str(datetime.datetime.now()),
                    "item": item,
                }
                json.dump(obj, f, indent=4)
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
