import os
from typing import Generator

from minet.executors import HTTPThreadPoolExecutor

from src.api.models.work import CreativeWork

BASE = "https://api.crossref.org/works?sample=100"
SELECT_FILTER = "&select=DOI%2Cmember%2Cdeposited%2Ccreated%2Ctype%2Creferences-count%2Cis-referenced-by-count"


class Client:
    """
    High-level Python API client for the Crossref API and for collecting \
        select data according to pre-defined models.
    """

    def __init__(self, mailto: str | None = None) -> None:
        """
        Prepare for the client to specify a user-agent in the API call.

        Args:
            mailto (str | None, optional): The email address to add to the \
                URI. Defaults to None.
        """
        if not mailto:
            mailto = os.environ.get("MAILTO")
        if mailto:
            mailto = mailto.replace("@", "%40")
            self.mailto = f"&mailto={mailto}"
        else:
            self.mailto = ""

    def build_works_endpoint(self, has_references: bool) -> str:
        """
        Build the URI for collecting select metadata from samples of works. \
            The samples are defined by whether the work has references.

        Args:
            has_references (bool): Value of the API's has-references filter.

        Returns:
            str: URI for the API request.
        """

        ref_filter = "&filter=has-references%3A"
        if has_references:
            ref_filter += "1"
        else:
            ref_filter += "0"
        return BASE + self.mailto + SELECT_FILTER + ref_filter

    def get_samples(
        self,
        has_references: bool,
        n: int = 10,
    ) -> Generator[list[CreativeWork], None, None]:
        """
        Collect samples of works from the API, and as each sample is \
            returned, model the works' metadata and yeild the modelled batch.

        Args:
            has_references (bool): Value of the API's has-references filter.
            n (int, optional): Number of samples. Defaults to 10.

        Yields:
            Generator[list[CreativeWork], None, None]: Modelled works metadata.
        """

        url = self.build_works_endpoint(has_references=has_references)
        urls = [url] * n
        with HTTPThreadPoolExecutor() as executor:
            for result in executor.request(urls):
                if result.response.status == 200:
                    # Parse the API response
                    items = result.response.json()["message"]["items"]
                    records = [
                        CreativeWork.load_json(item=i, has_refs=has_references)
                        for i in items
                    ]
                    yield records
