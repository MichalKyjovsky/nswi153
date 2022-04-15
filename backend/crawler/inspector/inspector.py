from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
import json


class Inspector(object):

    def __init__(self):
        super().__init__()

    @classmethod
    def _handle_urls(cls, urls, new_urls, processed_urls, boundary_regex, cur_obj, filtered_urls, base_url):
        for i in urls:
            if i not in new_urls and i not in processed_urls and re.match(rf'{boundary_regex}', i):
                new_urls.append(i)
            elif not re.match(rf'{boundary_regex}', i) and base_url != i:
                filtered_urls.add(i)

            if i != cur_obj["url"]:
                cur_obj["executionTargets"].append(i)

    @classmethod
    def crawl_url(cls, base_url: str, boundary_regex: str):
        """
        TODO: Add comment

        >>> Inspector.crawl_url("https://scrapethissite.com", "")
        ['https://scrapethissite.com', 'https://scrapethissite.com/', 'https://scrapethissite.com/faq/', 'https://scrapethissite.com/lessons/', 'https://scrapethissite.com/login/', 'https://scrapethissite.com/pages/', 'https://scrapethissite.com/pages/advanced/', 'https://scrapethissite.com/pages/advanced/?gotcha=csrf', 'https://scrapethissite.com/pages/advanced/?gotcha=headers', 'https://scrapethissite.com/pages/advanced/?gotcha=login', 'https://scrapethissite.com/pages/ajax-javascript/', 'https://scrapethissite.com/pages/forms/', 'https://scrapethissite.com/pages/forms/?page_num=1', 'https://scrapethissite.com/pages/forms/?page_num=10', 'https://scrapethissite.com/pages/forms/?page_num=11', 'https://scrapethissite.com/pages/forms/?page_num=12', 'https://scrapethissite.com/pages/forms/?page_num=13', 'https://scrapethissite.com/pages/forms/?page_num=14', 'https://scrapethissite.com/pages/forms/?page_num=15', 'https://scrapethissite.com/pages/forms/?page_num=16', 'https://scrapethissite.com/pages/forms/?page_num=17', 'https://scrapethissite.com/pages/forms/?page_num=18', 'https://scrapethissite.com/pages/forms/?page_num=19', 'https://scrapethissite.com/pages/forms/?page_num=2', 'https://scrapethissite.com/pages/forms/?page_num=20', 'https://scrapethissite.com/pages/forms/?page_num=21', 'https://scrapethissite.com/pages/forms/?page_num=22', 'https://scrapethissite.com/pages/forms/?page_num=23', 'https://scrapethissite.com/pages/forms/?page_num=24', 'https://scrapethissite.com/pages/forms/?page_num=3', 'https://scrapethissite.com/pages/forms/?page_num=4', 'https://scrapethissite.com/pages/forms/?page_num=5', 'https://scrapethissite.com/pages/forms/?page_num=6', 'https://scrapethissite.com/pages/forms/?page_num=7', 'https://scrapethissite.com/pages/forms/?page_num=8', 'https://scrapethissite.com/pages/forms/?page_num=9', 'https://scrapethissite.com/pages/frames/', 'https://scrapethissite.com/pages/simple/', 'https://scrapethissite.com/robots.txt']


        """

        out_dump = []

        new_urls = deque([base_url])

        processed_urls = set()

        # a set of domains inside the target website
        local_urls = set()
        # a set of domains outside the target website
        foreign_urls = set()
        # a set of broken urls
        broken_urls = set()

        filtered_urls = set()

        while len(new_urls):
            url = new_urls.popleft()
            processed_urls.add(url)
            # print the current url
            # print("Processing % s" % url)

            try:
                response = requests.get(url)
            except(
                    requests.exceptions.MissingSchema, requests.exceptions.ConnectionError,
                    requests.exceptions.InvalidURL,
                    requests.exceptions.InvalidSchema):
                # add broken urls to it’s own set, then continue
                broken_urls.add(url)
                continue

            # extract base url to resolve relative links
            parts = urlsplit(url)
            base = "{0.netloc}".format(parts)
            strip_base = base.replace("www.", "")
            base_url = "{0.scheme}://{0.netloc}".format(parts)
            path = url[:url.rfind('/') + 1] if ' / ' in parts.path else url

            cur_obj = {"url": url, "domain": base, "executionTargets": []}

            soup = BeautifulSoup(response.text, "lxml")

            for link in soup.find_all('a'):
                # extract link url from the anchor
                anchor = link.attrs["href"] if "href" in link.attrs else ''

                if anchor.startswith('#') or 'mailto' in anchor:
                    continue
                elif anchor.startswith('/'):
                    local_link = base_url + anchor
                    local_urls.add(local_link)
                elif strip_base in anchor:
                    local_urls.add(anchor)
                elif not anchor.startswith('http'):
                    local_link = path + anchor
                    local_urls.add(local_link)
                else:
                    foreign_urls.add(anchor)

            cls._handle_urls(local_urls, new_urls, processed_urls, boundary_regex, cur_obj, filtered_urls, base_url)
            cls._handle_urls(foreign_urls, new_urls, processed_urls, boundary_regex, cur_obj, filtered_urls, base_url)

            out_dump.append(cur_obj)

        out_dump = out_dump + [
            {"url": x, "domain": "{0.netloc}".format(urlsplit(x)), "executionTargets": []} for x
            in filtered_urls]

        return json.dumps(out_dump)


if __name__ == '__main__':
    print(Inspector.crawl_url("https://scrapethissite.com/", ".*(scrapethissite.com/lessons/|gum.co.*)$"))
