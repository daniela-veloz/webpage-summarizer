from backend.web_crawler import WebUrlCrawler
from backend.llm_client import LLMClient


class WebpageSummarizer:
    """
    Main service for webpage summarization.
    
    This class orchestrates the process of crawling a webpage and generating
    an AI-powered summary. It combines the WebUrlCrawler for content extraction
    and LLMClient for text generation.
    
    Attributes:
        model (str): The language model to use for summarization
        crawler (WebUrlCrawler): Instance for crawling web content
        llm_client (LLMClient): Instance for generating summaries
    """
    def __init__(self, model="gpt-4o-mini"):
        """
        Initialize the webpage summarizer.
        
        Args:
            model (str): The OpenAI model to use for summarization.
                        Defaults to 'gpt-4o-mini'.
        """
        self.model = model
        self.crawler = WebUrlCrawler()
        self.llm_client = LLMClient(model=model)
    
    def summarize(self, url: str) -> str:
        """
        Crawl a webpage and generate an AI-powered summary.
        
        This method combines web crawling and LLM-based text generation to create
        a comprehensive summary of the webpage content. The summary includes a
        TL;DR section and is formatted in markdown.
        
        Args:
            url (str): The URL of the webpage to summarize
            
        Returns:
            str: The generated summary in markdown format with TL;DR section
            
        Raises:
            requests.RequestException: If webpage crawling fails
            openai.OpenAIError: If LLM text generation fails
        """
        # Crawl the website
        website = self.crawler.crawl(url)
        
        # Generate summary
        system_prompt = """You are a web page summarizer that analyzes the content of a provided web page and provides a short and relevant summary. You will also provide a TL;DR at the top. Return your response in markdown."""
        user_prompt = f"""You are looking at the website titled: {website.title}. The content of the website is as follows: {website.body}."""
        
        summary = self.llm_client.generate_text(system_prompt=system_prompt, user_prompt=user_prompt)
        
        return summary