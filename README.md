---
title: WebPage Summarizer
emoji: 🌐
colorFrom: blue
colorTo: green
sdk: streamlit
sdk_version: 1.28.0
app_file: app.py
pinned: false
license: mit
---

# 🌐 WebPage Summarizer

An intelligent web content summarization tool that extracts and condenses webpage information using advanced AI models.

## 📋 Overview

This application creates concise, structured summaries of web content by leveraging state-of-the-art language models and robust web scraping techniques. Perfect for quickly understanding lengthy articles, blog posts, or documentation.

## ✨ Key Features

- **AI-Powered**: Powered by OpenAI's `gpt-4o-mini` model
- **Advanced Web Scraping**: Uses BeautifulSoup to handle static websites efficiently
- **Easy Interface**: Modern Streamlit web interface for immediate use
- **Smart Caching**: Repeated URLs use cached results for instant responses
- **Rate Limiting**: Fair usage limits with IP-based tracking
- **Security**: Robust IP extraction and request validation
- **Modular Architecture**: Clean separation of concerns for maintainability

## 🛠️ Technology Stack

- **AI Model**: OpenAI GPT-4o-mini
- **Web Scraping**: BeautifulSoup, Python Requests  
- **Interface**: Streamlit
- **AI Integration**: OpenAI API
- **Caching**: File-based caching system
- **Rate Limiting**: IP-based rate limiting with persistent storage
- **Architecture**: Modular backend with clean separation of concerns

## 🏗️ Architecture

```
┌───────────────────────────────────────────────────────────────┐
│                  Streamlit Web Interface                      │
│                        (app.py)                               │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│                 UI Message Handler                            │
│              (ui/message_handler.py)                          │
                                                                │
│  • Format user-facing messages                                │
│  • Handle error presentation                                  │
│  • Manage UI text and emojis                                  │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│                   Backend Services                            │
├───────────────────────────────────────────────────────────────┤
│  ┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐│
│  │  Rate Limiter   │  │   URL Cache     │  │ Webpage         ││
│  │  • IP tracking  │  │  • File-based   │  │ Summarizer      ││
│  │  • Cooldowns    │  │  • Fast lookup  │  │ • Orchestrates  ││
│  │  • Usage limits │  │  • TTL support  │  │   crawling      ││
│  └─────────────────┘  └─────────────────┘  │ • LLM summary   ││
│                                            └─────────────────┘│
│  ┌─────────────────┐  ┌─────────────────┐                     │
│  │  IP Extractor   │  │  Web Crawler    │                     │
│  │  • Client IP    │  │  • BeautifulSoup│                     │
│  │  • Header parse │  │  • Content clean│                     │
│  │  • Proxy support│  │  • Link extract │                     │
│  └─────────────────┘  └─────────────────┘                     │
└─────────────────────┬─────────────────────────────────────────┘
                      │
┌─────────────────────▼─────────────────────────────────────────┐
│                 External Services                             │
│  ┌─────────────────┐              ┌─────────────────┐         │
│  │   OpenAI API    │              │  Web Content    │         │
│  │  (GPT-4o-mini)  │              │   (Target URLs) │         │
│  └─────────────────┘              └─────────────────┘         │
└───────────────────────────────────────────────────────────────┘
```

### Component Responsibilities

- **UI Layer**: Handles all user-facing text, formatting, and presentation
- **Backend Services**: Pure business logic and data processing
- **Rate Limiting**: IP-based request throttling with persistent storage
- **Caching**: Fast retrieval of previously processed URLs
- **Web Crawling**: Content extraction and cleaning
- **IP Extraction**: Robust client identification for rate limiting

## 🚀 Usage

### Rate Limits
- **10 requests per hour** per user
- **25 requests per day** per user  
- **60 seconds cooldown** between requests
- **Cached results don't count** against your limits!

### How to Use
1. **Enter URL**: Paste the webpage URL you want to summarize
2. **Get Summary**: Click "Summarize" to receive an intelligent markdown summary

## 🎯 Perfect For

- **News Articles**: Quickly digest lengthy news content
- **Research Papers**: Extract key points from academic materials
- **Documentation**: Summarize technical documentation
- **Business Reports**: Extract insights from corporate content

## 🚀 Running Locally

### Prerequisites
- Python 3.7 or higher
- pip (Python package installer)

### Installation Steps
1. **Clone the repository** (if not already done)
2. **Install dependencies**:
   ```bash
   pip install -r requirements.txt
   ```
3. **Set up environment variables** (create a `.env` file or export):
   ```bash
   export OPENAI_API_KEY="your-api-key-here"
   ```
4. **Run the application**:
   ```bash
   streamlit run app.py
   ```
5. **Access the web interface**: Open your browser to the URL shown in the terminal (typically `http://localhost:8501`)

## 🔧 Setup Requirements

Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

## 📝 Examples

Try these sample URLs:
- https://en.wikipedia.org/wiki/Marie_Curie
- https://en.wikipedia.org/wiki/Artificial_intelligence

## 🔧 Technical Details

### Backend Components

#### Rate Limiter (`backend/rate_limiter.py`)
- **RateLimitResult**: Data class with semantic limit types (COOLDOWN, HOURLY_LIMIT, DAILY_LIMIT)
- **IP-based tracking**: Persistent storage in `.rate_limits/` directory
- **Configurable limits**: Environment variable support for customization

#### Caching System (`backend/cache.py`)
- **File-based storage**: Efficient caching with TTL support
- **Cache directory**: `.cache/` for storing processed summaries
- **Performance optimization**: Instant responses for repeated URLs

#### Web Crawler (`backend/web_crawler.py`)
- **Content extraction**: BeautifulSoup-based HTML parsing
- **Content cleaning**: Removes scripts, styles, and irrelevant elements
- **Robust handling**: User-agent headers and error recovery

#### IP Extractor (`backend/ip_extractor.py`)
- **Multi-source IP detection**: Direct client IP and proxy headers
- **Proxy support**: Handles X-Forwarded-For, X-Real-IP, CF-Connecting-IP
- **Fallback handling**: Graceful degradation to localhost

#### Webpage Summarizer (`backend/webpage_summarizer.py`)
- **Orchestration**: Coordinates web crawling and LLM processing
- **Clean interface**: Single method for URL-to-summary conversion
- **Configurable model**: Support for different OpenAI models

### UI Components

#### Message Handler (`ui/message_handler.py`)
- **Separation of concerns**: All user-facing text isolated from backend
- **Semantic formatting**: Uses backend data structures for presentation
- **Consistent messaging**: Standardized error, success, and info messages

### Data Flow
1. **Request**: User submits URL via Streamlit interface
2. **Cache Check**: System checks for existing summary
3. **Rate Limiting**: IP-based validation with structured results
4. **Processing**: Web crawling and LLM summarization
5. **Caching**: Store result for future requests
6. **Response**: Formatted message with usage statistics

## 💡 Tips

- Works best with content-rich pages (articles, blogs, documentation)
- Summaries include TL;DR sections for quick insights
- Cached results provide instant responses
- Rate limits reset hourly/daily for fair usage

## 📞 Contact

**Developer:** [Daniela Veloz](https://www.linkedin.com/in/daniela-veloz/)

Connect on LinkedIn for questions, feedback, or collaboration opportunities!

## 🔄 Auto-Sync

This repository automatically syncs with [Hugging Face Space](https://huggingface.co/spaces/daniela-veloz/WebSummarizer) on every push to main.


