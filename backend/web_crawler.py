import requests
from bs4 import BeautifulSoup
from backend.website import WebSite


class WebUrlCrawler:
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    def __init__(self, headless=True, timeout=10):
        self.timeout = timeout
        self.driver = None
        self.headless = headless

    def crawl(self, url) -> WebSite:
        response = requests.get(url, headers=self.headers, timeout=self.timeout)
        soup = BeautifulSoup(response.content, 'html.parser')
        title = soup.title.string if soup.title else "No title found"

        if soup.body:
            for irrelevant in soup.body(["script", "style", "img", "input"]):
                irrelevant.decompose()
            body = soup.body.get_text(strip=True, separator='\n')
        else:
            body = ""

        links = [link.get('href') for link in soup.find_all('a')]
        links = [link for link in links if link]

        return WebSite(url, title, body, links)