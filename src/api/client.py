import os

from minet.executors import HTTPThreadPoolExecutor

from src.api.models.work import CreativeWork

BASE = "https://api.crossref.org/works?sample=100"
SELECT_FILTER = "&select=DOI%2Cmember%2Cdeposited%2Ccreated%2Ctype%2Creferences-count%2Cis-referenced-by-count"


class Client:
    def __init__(self, mailto: str | None = None) -> None:
        """
        __init__ _summary_

        Args:
            mailto (str | None, optional): The email address to add to the \
                URL. Defaults to None.
        """
        if not mailto:
            mailto = os.environ.get("MAILTO")
        if mailto:
            mailto = mailto.replace("@", "%40")
            self.mailto = f"&mailto={mailto}"
        else:
            self.mailto = ""

    def build_url(self, has_references: bool) -> str:
        ref_filter = "&filter=has-references%3A"
        if has_references:
            ref_filter += "1"
        else:
            ref_filter += "0"
        return BASE + self.mailto + SELECT_FILTER + ref_filter

    def get_samples(self, has_references: bool, n: int = 10):
        url = self.build_url(has_references=has_references)
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
