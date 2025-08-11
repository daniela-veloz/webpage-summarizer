import os
import gradio as gr
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from openai import OpenAI
import hashlib
import json
from pathlib import Path
import time

class WebSite:
    def __init__(self, url, title, body, links):
        self.url = url
        self.title = title
        self.body = body
        self.links = links

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

class RateLimiter:
    def __init__(self, rate_dir=".rate_limits"):
        self.rate_dir = Path(rate_dir)
        self.rate_dir.mkdir(exist_ok=True)
        
        # Configuration from environment variables with defaults
        self.hourly_limit = int(os.getenv('HOURLY_LIMIT', '10'))
        self.daily_limit = int(os.getenv('DAILY_LIMIT', '25'))
        self.cooldown_seconds = int(os.getenv('COOLDOWN_SECONDS', '60'))
    
    def _get_ip_file(self, ip_address):
        # Clean IP for filename (replace dots/colons with underscores)
        clean_ip = ip_address.replace('.', '_').replace(':', '_')
        return self.rate_dir / f"ip_{clean_ip}.json"
    
    def _get_current_time(self):
        return time.time()
    
    def _cleanup_old_requests(self, requests_data, current_time):
        """Remove requests older than 24 hours"""
        cutoff_time = current_time - (24 * 3600)  # 24 hours ago
        return [req_time for req_time in requests_data if req_time > cutoff_time]
    
    def check_rate_limit(self, ip_address):
        """Check if IP address is within rate limits. Returns (allowed, message, stats)"""
        current_time = self._get_current_time()
        ip_file = self._get_ip_file(ip_address)
        
        # Load existing data or create new
        if ip_file.exists():
            try:
                with open(ip_file, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = {'requests': [], 'last_request': 0}
        else:
            data = {'requests': [], 'last_request': 0}
        
        # Clean up old requests
        data['requests'] = self._cleanup_old_requests(data['requests'], current_time)
        
        # Check cooldown period
        if current_time - data.get('last_request', 0) < self.cooldown_seconds:
            remaining_cooldown = int(self.cooldown_seconds - (current_time - data['last_request']))
            return False, f"⏰ Please wait {remaining_cooldown} seconds between requests", self._get_usage_stats(data['requests'], current_time)
        
        # Check hourly limit
        hour_ago = current_time - 3600
        hourly_requests = [req for req in data['requests'] if req > hour_ago]
        
        if len(hourly_requests) >= self.hourly_limit:
            next_reset = int((min(hourly_requests) + 3600 - current_time) / 60)
            return False, f"🚫 Hourly limit reached ({self.hourly_limit} requests/hour). Try again in {next_reset} minutes.", self._get_usage_stats(data['requests'], current_time)
        
        # Check daily limit
        if len(data['requests']) >= self.daily_limit:
            next_reset = int((min(data['requests']) + 24*3600 - current_time) / 3600)
            return False, f"🚫 Daily limit reached ({self.daily_limit} requests/day). Try again in {next_reset} hours.", self._get_usage_stats(data['requests'], current_time)
        
        return True, "✅ Request allowed", self._get_usage_stats(data['requests'], current_time)
    
    def record_request(self, ip_address):
        """Record a new request for the IP address"""
        current_time = self._get_current_time()
        ip_file = self._get_ip_file(ip_address)
        
        # Load existing data
        if ip_file.exists():
            try:
                with open(ip_file, 'r') as f:
                    data = json.load(f)
            except (json.JSONDecodeError, FileNotFoundError):
                data = {'requests': [], 'last_request': 0}
        else:
            data = {'requests': [], 'last_request': 0}
        
        # Add new request and update last request time
        data['requests'].append(current_time)
        data['last_request'] = current_time
        
        # Clean up old requests
        data['requests'] = self._cleanup_old_requests(data['requests'], current_time)
        
        # Save updated data
        try:
            with open(ip_file, 'w') as f:
                json.dump(data, f)
        except Exception as e:
            print(f"Warning: Could not save rate limit data: {e}")
    
    def _get_usage_stats(self, requests, current_time):
        """Get current usage statistics"""
        hour_ago = current_time - 3600
        hourly_count = len([req for req in requests if req > hour_ago])
        daily_count = len(requests)
        
        return {
            'hourly_used': hourly_count,
            'hourly_limit': self.hourly_limit,
            'daily_used': daily_count,
            'daily_limit': self.daily_limit,
            'hourly_remaining': max(0, self.hourly_limit - hourly_count),
            'daily_remaining': max(0, self.daily_limit - daily_count)
        }

class URLCache:
    def __init__(self, cache_dir=".cache", cache_hours=24):
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(exist_ok=True)
        self.cache_hours = cache_hours
    
    def _get_cache_key(self, url):
        return hashlib.md5(url.encode()).hexdigest()
    
    def _get_cache_file(self, cache_key):
        return self.cache_dir / f"{cache_key}.json"
    
    def get(self, url):
        cache_key = self._get_cache_key(url)
        cache_file = self._get_cache_file(cache_key)
        
        if not cache_file.exists():
            return None
        
        try:
            with open(cache_file, 'r', encoding='utf-8') as f:
                data = json.load(f)
            
            # Check if cache has expired
            cache_time = data.get('timestamp', 0)
            current_time = time.time()
            
            if current_time - cache_time > (self.cache_hours * 3600):
                cache_file.unlink()  # Delete expired cache
                return None
            
            return data.get('summary')
        except (json.JSONDecodeError, KeyError):
            # If cache file is corrupted, delete it
            if cache_file.exists():
                cache_file.unlink()
            return None
    
    def set(self, url, summary):
        cache_key = self._get_cache_key(url)
        cache_file = self._get_cache_file(cache_key)
        
        data = {
            'url': url,
            'summary': summary,
            'timestamp': time.time()
        }
        
        try:
            with open(cache_file, 'w', encoding='utf-8') as f:
                json.dump(data, f, ensure_ascii=False, indent=2)
        except Exception as e:
            # If we can't write to cache, just continue without caching
            print(f"Warning: Could not write to cache: {e}")

class LLMClient:
    def __init__(self, model):
        self.model = model
        self.openai = OpenAI()

    def generate_text(self, user_prompt, system_prompt="") -> str:
        messages = [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ]
        response = self.openai.chat.completions.create(
            model=self.model,
            messages=messages,
        )
        return response.choices[0].message.content

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
            return f"📋 **Cached Result** (no API cost!)\n\n{cached_summary}"
        
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
        - 🤖 **AI-Powered**: Uses OpenAI GPT-4o-mini for intelligent summaries
        - 🕷️ **Smart Web Scraping**: Handles static web content efficiently
        - 📝 **Markdown Output**: Clean, formatted summaries
        - 📋 **Smart Caching**: Repeated URLs use cached results (no extra cost!)
        - 🛡️ **Rate Limited**: Fair usage limits protect against abuse
        
        ### 🚀 How to use:
        1. Enter a webpage URL
        2. Click "Summarize" to get an intelligent summary
        
        ### ⏱️ Usage Limits:
        - **10 requests per hour** per user
        - **25 requests per day** per user  
        - **60 seconds cooldown** between requests
        - 📋 **Cached results don't count** against your limits!
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                url_input = gr.Textbox(
                    label="📎 Enter Webpage URL",
                    placeholder="https://example.com/article",
                    lines=1
                )
                
                
                summarize_btn = gr.Button("📋 Summarize", variant="primary")
            
            with gr.Column(scale=4):
                output = gr.Markdown(
                    label="📄 Summary",
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
        
        ### 🔧 Environment Configuration:
        Set these environment variables to customize limits:
        - `HOURLY_LIMIT`: Requests per hour (default: 10)
        - `DAILY_LIMIT`: Requests per day (default: 25)
        - `COOLDOWN_SECONDS`: Seconds between requests (default: 60)
        """)
    
    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch()