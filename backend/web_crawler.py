import requests
from bs4 import BeautifulSoup
from backend.website import WebSite


class WebUrlCrawler:
    """
    Web crawler for extracting content from web pages.
    
    This class handles HTTP requests to web pages, parses HTML content using BeautifulSoup,
    and extracts relevant information including title, body text, and links while removing
    irrelevant elements like scripts, styles, and images.
    
    Attributes:
        headers (dict): HTTP headers to use for requests, including User-Agent
        timeout (int): Request timeout in seconds
        driver: Placeholder for future browser automation (currently unused)
        headless (bool): Browser mode setting (currently unused)
    """
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/117.0.0.0 Safari/537.36"
    }

    def __init__(self, headless=True, timeout=10):
        """
        Initialize the web crawler.
        
        Args:
            headless (bool): Browser headless mode (currently unused, defaults to True)
            timeout (int): Request timeout in seconds (defaults to 10)
        """
        self.timeout = timeout
        self.driver = None
        self.headless = headless

    def crawl(self, url) -> WebSite:
        """
        Crawl a webpage and extract its content.
        
        This method sends an HTTP GET request to the specified URL, parses the HTML content,
        extracts the title and body text while removing irrelevant elements (scripts, styles,
        images, inputs), and collects all links found on the page.
        
        Args:
            url (str): The URL to crawl
            
        Returns:
            WebSite: A WebSite object containing the extracted content
            
        Raises:
            requests.RequestException: If the HTTP request fails
            requests.Timeout: If the request times out
        """
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