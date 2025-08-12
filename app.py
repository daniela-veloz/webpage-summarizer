import streamlit as st
from dotenv import load_dotenv
import time

from backend.rate_limiter import RateLimiter
from backend.cache import URLCache
from backend.ip_extractor import IPExtractor
from backend.webpage_summarizer import WebpageSummarizer
from ui.message_handler import UIMessageHandler

# Load environment variables
load_dotenv()


# Initialize global components
@st.cache_resource
def get_cache():
    return URLCache()


@st.cache_resource
def get_rate_limiter():
    return RateLimiter()


@st.cache_resource
def get_webpage_summarizer():
    return WebpageSummarizer()


# Get singletons
cache = get_cache()
rate_limiter = get_rate_limiter()
webpage_summarizer = get_webpage_summarizer()


def summarize_webpage(url: str) -> str:
    """Summarize a webpage URL and return formatted result"""
    try:
        # Get client IP address
        client_ip = IPExtractor.get_client_ip()

        # Check cache first (cached requests don't count against rate limit)
        cached_summary = cache.get(url)
        if cached_summary:
            return UIMessageHandler.format_cached_result(cached_summary)

        # Check rate limit for new requests
        rate_limit_result = rate_limiter.check_rate_limit()
        if not rate_limit_result.valid:
            return UIMessageHandler.format_rate_limit_error(rate_limit_result)

        # Record the request
        rate_limiter.record_request(client_ip)

        # Generate summary using the summarizer
        summary = webpage_summarizer.summarize(url)

        # Cache the result
        cache.set(url, summary)

        # Add usage stats to response using the stats from the rate limit check
        return UIMessageHandler.format_summary_with_stats(summary, rate_limit_result.stats)

    except Exception as e:
        return UIMessageHandler.format_error(e)


def main():
    # Page configuration
    st.set_page_config(
        page_title="🌐 WebPage Summarizer",
        page_icon="🌐",
        layout="wide",
        initial_sidebar_state="collapsed"
    )

    # Main header
    st.title("🌐 WebPage Summarizer")
    st.markdown(
        "An intelligent web content summarization tool that extracts and condenses webpage information using advanced AI models.")

    # How to use and Usage Limits in same row
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        ### 🚀 How to use:
        1. Enter a webpage URL
        2. Click 'Summarize' to get an intelligent summary
        """)
    with col2:
        st.markdown("""
        ### ⏱️ Usage Limits:
        - **10 requests per hour** per user
        - **25 requests per day** per user  
        - **60 seconds cooldown** between requests
        - **Cached results don't count** against your limits!
        """)

    st.markdown("")  # Add spacing

    # URL input
    url_input = st.text_input(
        "📎 Enter Webpage URL",
        placeholder="https://example.com/article",
        help="Enter the URL of the webpage you want to summarize"
    )

    # Summarize button
    if st.button("📋 Summarize", type="primary", use_container_width=True):
        if url_input.strip():
            with st.spinner("Analyzing webpage..."):
                result = summarize_webpage(url_input.strip())
            st.markdown(result)
        else:
            st.error("Please enter a valid URL")

    # Examples section
    st.markdown("### 📝 Examples")
    example_urls = [
        "https://en.wikipedia.org/wiki/Marie_Curie",
        "https://en.wikipedia.org/wiki/Artificial_intelligence"
    ]

    # Display all buttons first
    selected_example = None
    for i, example_url in enumerate(example_urls):
        if st.button(f"Try: {example_url}", key=f"example_{i}"):
            selected_example = example_url
    
    # Display result below all buttons if one was clicked
    if selected_example:
        with st.spinner("Analyzing webpage..."):
            result = summarize_webpage(selected_example)
        st.markdown(result)

    # Tips section
    st.markdown("### 💡 Tips:")
    st.markdown("""
    - For best results, use URLs with substantial text content
    - The tool works best with articles, blog posts, and documentation
    - Repeated requests to the same URL are served instantly from cache
    - Rate limits reset every hour/day to ensure fair access for all users
    """)
    
    # Contact section
    st.markdown("---")
    st.markdown("### 📞 Contact")
    st.markdown("**Connect with the developer:** [Daniela Veloz on LinkedIn](https://www.linkedin.com/in/daniela-veloz/)")


if __name__ == "__main__":
    main()