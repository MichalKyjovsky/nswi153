from bs4 import BeautifulSoup
import requests
import requests.exceptions
from urllib.parse import urlsplit
from urllib.parse import urlparse
from collections import deque


class Inspector(object):

    def __init__(self):
        super().__init__()

    @classmethod
    def crawl_url(cls, url: str):
        """
        TODO: Add comment
        """
        new_urls = deque([url])

        processed_urls = set()

        # a set of domains inside the target website
        local_urls = set()
        # a set of domains outside the target website
        foreign_urls = set()
        # a set of broken urls
        broken_urls = set()
