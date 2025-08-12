import gradio as gr
from dotenv import load_dotenv
import time

from backend.web_crawler import WebUrlCrawler
from backend.rate_limiter import RateLimiter
from backend.cache import URLCache
from backend.llm_client import LLMClient

# Initialize global cache and rate limiter
cache = URLCache()
rate_limiter = RateLimiter()

def summarize_webpage(url, request: gr.Request = None):
    try:
        # Get client IP address
        client_ip = "127.0.0.1"  # Default fallback
        if request and hasattr(request, 'client') and request.client:
            client_ip = request.client.host
        elif request and hasattr(request, 'headers'):
            # Try to get real IP from headers (for Hugging Face Spaces)
            client_ip = (
                request.headers.get('x-forwarded-for', '').split(',')[0].strip() or
                request.headers.get('x-real-ip', '').strip() or
                request.headers.get('cf-connecting-ip', '').strip() or
                "127.0.0.1"
            )
        
        # Check cache first (cached requests don't count against rate limit)
        cached_summary = cache.get(url)
        if cached_summary:
            return f"📋 **Cached Result** \n\n{cached_summary}"
        
        # Check rate limit for new requests
        allowed, message, stats = rate_limiter.check_rate_limit(client_ip)
        if not allowed:
            return f"{message}\n\n**Your current usage:**\n- Hourly: {stats['hourly_used']}/{stats['hourly_limit']} (remaining: {stats['hourly_remaining']})\n- Daily: {stats['daily_used']}/{stats['daily_limit']} (remaining: {stats['daily_remaining']})\n\n*💡 Tip: Repeated requests to the same URL use cached results and don't count against your limit!*"
        
        # Record the request
        rate_limiter.record_request(client_ip)
        
        # Initialize crawler and LLM client
        crawler = WebUrlCrawler()
        llm_client = LLMClient(model="gpt-4o-mini")
        
        # Crawl the website
        website = crawler.crawl(url)
        
        # Generate summary
        system_prompt = """You are a web page summarizer that analyzes the content of a provided web page and provides a short and relevant summary. You will also provide a TL;DR at the top. Return your response in markdown."""
        user_prompt = f"""You are looking at the website titled: {website.title}. The content of the website is as follows: {website.body}."""
        
        summary = llm_client.generate_text(system_prompt=system_prompt, user_prompt=user_prompt)
        
        # Cache the result
        cache.set(url, summary)
        
        # Add usage stats to response
        updated_stats = rate_limiter._get_usage_stats(
            [time.time()] + rate_limiter._cleanup_old_requests([], time.time()), 
            time.time()
        )
        
        return f"{summary}\n\n---\n*📊 Usage: {updated_stats['hourly_used']}/{updated_stats['hourly_limit']} hourly, {updated_stats['daily_used']}/{updated_stats['daily_limit']} daily*"
        
    except Exception as e:
        return f"Error processing URL: {str(e)}"

# Load environment variables
load_dotenv()

# Create Gradio interface
def main():
    with gr.Blocks(title="🌐 WebPage Summarizer", theme=gr.themes.Soft()) as demo:
        gr.Markdown("""
        # 🌐 WebPage Summarizer
        
        An intelligent web content summarization tool that extracts and condenses webpage information using advanced AI models.
        
        ### ✨ Features:
        - **AI-Powered**: Uses OpenAI GPT-4o-mini for intelligent summaries
        - **Smart Web Scraping**: Handles static web content efficiently
        - **Smart Caching**: Repeated URLs use cached results
        - **Rate Limited**: Fair usage limits protect against abuse
        
        ### 🚀 How to use:
        1. Enter a webpage URL
        2. Click "Summarize" to get an intelligent summary
        
        ### ⏱️ Usage Limits:
        - **10 requests per hour** per user
        - **25 requests per day** per user  
        - **60 seconds cooldown** between requests
        - **Cached results don't count** against your limits!
        """)
        
        url_input = gr.Textbox(
            label="📎 Enter Webpage URL",
            placeholder="https://example.com/article",
            lines=1
        )
        
        summarize_btn = gr.Button("📋 Summarize", variant="primary")
        
        output = gr.Markdown(
            label="Summary",
            value="Enter a URL and click 'Summarize' to get started!"
        )
        
        # Event handlers
        summarize_btn.click(
            fn=summarize_webpage,
            inputs=[url_input],
            outputs=output
        )
        
        # Examples
        gr.Examples(
            examples=[
                ["https://en.wikipedia.org/wiki/Marie_Curie"],
                ["https://en.wikipedia.org/wiki/Artificial_intelligence"],
            ],
            inputs=[url_input]
        )
        
        gr.Markdown("""
        ### 💡 Tips:
        - For best results, use URLs with substantial text content
        - The tool works best with articles, blog posts, and documentation
        - Repeated requests to the same URL are served instantly from cache
        - Rate limits reset every hour/day to ensure fair access for all users
    
        """)
    
    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch()