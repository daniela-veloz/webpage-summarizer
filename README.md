---
title: WebPage Summarizer
emoji: 🌐
colorFrom: blue
colorTo: green
sdk: gradio
sdk_version: 4.44.0
app_file: app.py
pinned: false
license: mit
---

# 🌐 WebPage Summarizer

An intelligent web content summarization tool that extracts and condenses webpage information using advanced AI models.

## 📋 Overview

This application creates concise, structured summaries of web content by leveraging state-of-the-art language models and robust web scraping techniques. Perfect for quickly understanding lengthy articles, blog posts, or documentation.

## ✨ Key Features

- **🤖 Dual AI Models**: Powered by OpenAI's `gpt-4o-mini` and open-source `gpt-oss:20b` through Ollama
- **🕷️ Advanced Web Scraping**: Uses BeautifulSoup to handle static websites efficiently
- **📝 Markdown Output**: Generates clean, formatted summaries in Markdown
- **🎯 Focused Processing**: Efficiently processes individual webpage URLs
- **🚀 Easy Interface**: Simple Gradio web interface for immediate use

## 🛠️ Technology Stack

- **AI Models**: OpenAI GPT-4o-mini, GPT-OSS:20B (local)
- **Web Scraping**: BeautifulSoup, Python Requests  
- **Interface**: Gradio
- **AI Integration**: OpenAI API, Ollama (for local models)

## 🚀 Usage

1. **Enter URL**: Paste the webpage URL you want to summarize
2. **Choose Model**: Select between OpenAI GPT-4o-mini or local GPT-OSS:20b
3. **Get Summary**: Click "Summarize" to receive an intelligent markdown summary

## 🎯 Perfect For

- **📰 News Articles**: Quickly digest lengthy news content
- **📚 Research Papers**: Extract key points from academic materials
- **📖 Documentation**: Summarize technical documentation
- **💼 Business Reports**: Extract insights from corporate content

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
   python app.py
   ```
5. **Access the web interface**: Open your browser to the URL shown in the terminal (typically `http://127.0.0.1:7860`)

## 🔧 Setup Requirements

### For OpenAI Models
Set your OpenAI API key as an environment variable:
```bash
export OPENAI_API_KEY="your-api-key-here"
```

### For Local GPT-OSS Models
1. Install [Ollama](https://ollama.com)
2. Pull the model: `ollama pull gpt-oss:20b`
3. Start Ollama service: `ollama serve`

## 📝 Examples

Try these sample URLs:
- https://en.wikipedia.org/wiki/Marie_Curie
- https://en.wikipedia.org/wiki/Artificial_intelligence

## 💡 Tips

- Works best with content-rich pages (articles, blogs, documentation)
- Local models require Ollama running on your system
- Summaries include TL;DR sections for quick insights


