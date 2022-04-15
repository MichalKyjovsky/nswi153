import unittest
import json

from crawler.core.inspector.inspector import Inspector


class CrawlerWorksCorrectlyTestCase(unittest.TestCase):
    def test_basic_crawl(self):
        rs = Inspector.crawl_url("https://scrapethissite.com/", ".*(scrapethissite.com/lessons/|gum.co.*)$")

        with open('test.json', mode="rt") as vp:
            vps = json.load(vp)
            self.assertEqual(vps, rs)


if __name__ == '__main__':
    unittest.main()
