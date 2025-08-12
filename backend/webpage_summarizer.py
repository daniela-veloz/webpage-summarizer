from backend.web_crawler import WebUrlCrawler
from backend.llm_client import LLMClient


class WebpageSummarizer:
    def __init__(self, model="gpt-4o-mini"):
        self.model = model
        self.crawler = WebUrlCrawler()
        self.llm_client = LLMClient(model=model)
    
    def summarize(self, url: str) -> str:
        """
        Crawl a webpage and generate a summary using LLM
        
        Args:
            url: The URL to summarize
            
        Returns:
            str: The generated summary
        """
        # Crawl the website
        website = self.crawler.crawl(url)
        
        # Generate summary
        system_prompt = """You are a web page summarizer that analyzes the content of a provided web page and provides a short and relevant summary. You will also provide a TL;DR at the top. Return your response in markdown."""
        user_prompt = f"""You are looking at the website titled: {website.title}. The content of the website is as follows: {website.body}."""
        
        summary = self.llm_client.generate_text(system_prompt=system_prompt, user_prompt=user_prompt)
        
        return summary