class WebSite:
    """
    Data structure representing a crawled webpage.
    
    This class holds the essential information extracted from a webpage,
    including its URL, title, main content, and links to other pages.
    
    Attributes:
        url (str): The URL of the webpage
        title (str): The title of the webpage
        body (str): The main text content of the webpage
        links (list): List of links found on the webpage
    """
    
    def __init__(self, url, title, body, links):
        """
        Initialize a WebSite instance.
        
        Args:
            url (str): The URL of the webpage
            title (str): The title of the webpage
            body (str): The main text content of the webpage
            links (list): List of links found on the webpage
        """
        self.url = url
        self.title = title
        self.body = body
        self.links = links