from django.test import TestCase
import json
from pathlib import Path

from core.inspector.inspector import Inspector


class CrawlerWorksCorrectlyTestCase(TestCase):
    def test_basic_crawl(self):
        rs = Inspector.crawl_url("https://scrapethissite.com/", ".*(scrapethissite.com/lessons/|gum.co.*)$")

        with open(Path(__file__).parent.joinpath('test.json'), mode="rt") as vp:
            vps = json.load(vp)
            self.assertEqual(vps, rs)
