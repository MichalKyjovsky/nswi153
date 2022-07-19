import datetime
import logging

from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from collections import deque
import re
from operator import itemgetter
from . import LOGGER


class Inspector(object):
    """
    The following class is responsible for web crawling of the particular website and constructing the JSON structure
    that reflects the Oriented Graph of crawled domains.
    """

    # Regex boundary for the crawled urls
    _boundary_regex = None

    def __init__(self):
        """
        Constructor method.
        """
        super().__init__()

    @classmethod
    def _matches_regex_boundary(cls, url: str) -> bool:
        """
        Verifies whether the URL about to be crawled matches the given boundary regex - if provided. If no boundary was
        set, then True is implicitly returned.
        Args:
            url: URL/domain about to be crawled.

        Returns:
            True if provided URL matches boundary regular expression or if the expression was not set. Else False.
        """
        return re.match(rf'{cls._boundary_regex}', url) if cls._boundary_regex else True

    @classmethod
    def _handle_urls(cls, urls: set, new_urls: deque, processed_urls: set, cur_node: dict, filtered_urls: set,
                     base_url: str) -> None:
        """
        Divides the provided urls into to groups - those to be processed and those that represents the leaf nodes
        and won't be visited.

        Args:
            urls: URLs to be categorized
            new_urls: Dequeue of the URLs to be visited.
            processed_urls: Set of URLs that were already processed.
            cur_node: Current URL/domain node.
            filtered_urls: Set of URLs/domains that represents leaf nodes and won't be visited at all.
            base_url: Base URL for the deduplication from the target set (each URL/domain node would have referenced
                      itself)
        """
        for url in urls:
            if url not in new_urls and url not in processed_urls and cls._matches_regex_boundary(url):
                new_urls.append(url)
            elif not cls._matches_regex_boundary(url) and base_url != url:
                filtered_urls.add(url)

            if url != cur_node["url"]:
                cur_node["execution_targets"].append(url)

    @classmethod
    def _inspect_url(cls, links: list, base_url: str, strip_base: str, path: str) -> set:
        """
        Handles the provided list of links, normalizes them and adds them for further processing.
        Args:
            links: List of links observed in the current iteration (crawled URL/domain)
            base_url: Full domain URL, i.e. https://example.com or https://www.example.com
            strip_base: Domain name, i.e. example.com
            path:  Base URL with ending slash '/'

        Returns:
            Set of the URLs/domains that will be subject to further filtering and processing if not processed yet.
        """
        urls_to_be_processed = set()

        for link in links:
            # extract link url from the anchor
            anchor = link.attrs["href"] if "href" in link.attrs else ''

            if anchor.startswith('#') or 'mailto' in anchor:
                continue
            elif anchor.startswith('/'):
                local_link = base_url + anchor
                urls_to_be_processed.add(local_link)
            elif strip_base in anchor:
                urls_to_be_processed.add(anchor)
            elif not anchor.startswith('http'):
                local_link = path + anchor
                urls_to_be_processed.add(local_link)
            else:
                urls_to_be_processed.add(anchor)

        return urls_to_be_processed

    @classmethod
    def crawl_url(cls, top_level_url: str, boundary_regex: str = None) -> list:
        """
        Crawls the provided top_level_url for all the links that is contains considering the provided boundary_regex
        expression.

        Args:
            top_level_url: URL to be crawled
            boundary_regex: Regular expression denoting the boundaries of the crawled URLs/domains.

        Returns:
            List of objects (dictionaries) representing the information about the nodes (crawled domains/URLs) and
            relations among them.
        """

        # Initialize the boundary
        cls._boundary_regex = boundary_regex

        # Output array of nodes (crawled websites)
        out_dump = []

        # Initialize the queue
        new_urls = deque([top_level_url])

        # Visited domains/urls
        processed_urls = set()

        # Set of domains inside the target website
        urls_to_be_processed = set()

        # Set of urls that won't be visited - Leafs
        filtered_urls = set()

        while len(new_urls):
            url = new_urls.popleft()
            processed_urls.add(url)

            LOGGER.log(logging.DEBUG, "Processing % s" % url)

            try:
                # Get the website
                response = requests.get(url)

                # Extract base url to resolve relative links
                parts = urlsplit(url)
                base = f"{parts.netloc}"
                strip_base = base.replace("www.", "")
                base_url = f"{parts.scheme}://{parts.netloc}"
                path = url[:url.rfind('/') + 1] if '/' in parts.path else url

                # Initialize current node
                cur_node = {"url": url, "domain": base, "execution_targets": [], "crawl_time": datetime.datetime.now(),
                            "boundary_record": False}

                soup = BeautifulSoup(response.text, "lxml")

                # Merge to be processed URLs with the current set of newly observed domains
                urls_to_be_processed = urls_to_be_processed.union(
                    cls._inspect_url(soup.find_all('a'), base_url, strip_base, path))

                website_title = soup.find('title')

                cur_node['title'] = website_title.text if website_title else None

                cls._handle_urls(urls_to_be_processed, new_urls, processed_urls, cur_node, filtered_urls, base_url)

                cur_node["execution_targets"] = sorted(cur_node["execution_targets"])

                # Add to result set
                out_dump.append(cur_node)

            except(
                    requests.exceptions.MissingSchema, requests.exceptions.ConnectionError,
                    requests.exceptions.InvalidURL,
                    requests.exceptions.InvalidSchema):

                LOGGER.log(logging.ERROR, "Failed to process % s" % url)

        # Add leaf nodes
        out_dump = out_dump + [
            {"url": x, "domain": f"{urlsplit(x).netloc}", "execution_targets": [],
             "crawl_time": datetime.datetime.now(),
             "title": f"{urlsplit(x).netloc}", "boundary_record": True}
            for x in
            filtered_urls]

        return sorted(out_dump, key=itemgetter("url"))
