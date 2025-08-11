import os
import gradio as gr
from dotenv import load_dotenv
import requests
from bs4 import BeautifulSoup
from openai import OpenAI

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

class LLMClient:
    def __init__(self, model, base_url=None):
        self.model = model
        if base_url:
            self.openai = OpenAI(base_url=base_url, api_key=model)
        else:
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

def summarize_webpage(url, model_choice):
    try:
        # Initialize crawler and LLM client based on model choice
        crawler = WebUrlCrawler()
        
        if model_choice == "OpenAI GPT-4o-mini":
            llm_client = LLMClient(model="gpt-4o-mini")
        else:  # Local GPT-OSS:20b
            llm_client = LLMClient(model="gpt-oss:20b", base_url="http://localhost:11434/v1")
        
        # Crawl the website
        website = crawler.crawl(url)
        
        # Generate summary
        system_prompt = """You are a web page summarizer that analyzes the content of a provided web page and provides a short and relevant summary. You will also provide a TL;DR at the top. Return your response in markdown."""
        user_prompt = f"""You are looking at the website titled: {website.title}. The content of the website is as follows: {website.body}."""
        
        summary = llm_client.generate_text(system_prompt=system_prompt, user_prompt=user_prompt)
        return summary
        
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
        - 🤖 **Dual AI Models**: OpenAI GPT-4o-mini or local GPT-OSS:20b
        - 🕷️ **Smart Web Scraping**: Handles both static and dynamic content
        - 📝 **Markdown Output**: Clean, formatted summaries
        
        ### 🚀 How to use:
        1. Enter a webpage URL
        2. Choose your AI model
        3. Click "Summarize" to get an intelligent summary
        """)
        
        with gr.Row():
            with gr.Column(scale=3):
                url_input = gr.Textbox(
                    label="📎 Enter Webpage URL",
                    placeholder="https://example.com/article",
                    lines=1
                )
                
                model_choice = gr.Radio(
                    choices=["OpenAI GPT-4o-mini", "Local GPT-OSS:20b"],
                    value="OpenAI GPT-4o-mini",
                    label="🤖 Choose AI Model"
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
            inputs=[url_input, model_choice],
            outputs=output
        )
        
        # Examples
        gr.Examples(
            examples=[
                ["https://en.wikipedia.org/wiki/Marie_Curie", "OpenAI GPT-4o-mini"],
                ["https://en.wikipedia.org/wiki/Artificial_intelligence", "OpenAI GPT-4o-mini"],
            ],
            inputs=[url_input, model_choice]
        )
        
        gr.Markdown("""
        ### 💡 Tips:
        - For best results, use URLs with substantial text content
        - Local GPT-OSS:20b requires Ollama to be running locally
        - The tool works best with articles, blog posts, and documentation
        """)
    
    return demo

if __name__ == "__main__":
    demo = main()
    demo.launch()