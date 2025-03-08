import unittest

from rich.progress import BarColumn, Progress, TimeElapsedColumn

from src.api.client import Client

MAILTO = "user@mail.com"

WITH_REFERENCES_URL = "https://api.crossref.org/works?sample=100&mailto=user%40mail.com&select=DOI%2Cmember%2Cdeposited%2Ccreated%2Ctype%2Creferences-count%2Cis-referenced-by-count&filter=has-references%3A1"
WITHOUT_REFERENCES_URL = "https://api.crossref.org/works?sample=100&mailto=user%40mail.com&select=DOI%2Cmember%2Cdeposited%2Ccreated%2Ctype%2Creferences-count%2Cis-referenced-by-count&filter=has-references%3A0"


class ClientTest(unittest.TestCase):
    def setUp(self):
        self.client = Client(mailto=MAILTO)

    def test_works_endpoint(self):
        """
        The client should build a URL that filters on whether or not works
        have references.
        """
        actual = self.client.build_works_endpoint(has_references=True)
        expected = WITH_REFERENCES_URL
        self.assertEqual(actual, expected)

        actual = self.client.build_works_endpoint(has_references=False)
        expected = WITHOUT_REFERENCES_URL
        self.assertEqual(actual, expected)

    def test_request(self):
        """
        The client should request and return 2 samples of 100 items each.
        """
        N = 2
        responses = []
        with Progress(BarColumn(), TimeElapsedColumn()) as p:
            t = p.add_task("", total=N)
            for records in self.client.get_samples(has_references=True, n=N):
                # Affirm that the returned sample has 100 items
                self.assertEqual(len(records), 100)
                # Append the response to a list
                responses.append(records)
                p.advance(t)
        # Affirm the list of responses has 2 objects
        self.assertEqual(len(responses), N)


if __name__ == "__main__":
    unittest.main()
