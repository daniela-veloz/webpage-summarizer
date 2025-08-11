# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Commands

### Running the Application
```bash
python app.py
```

### Installing Dependencies
```bash
pip install -r requirements.txt
```

### Environment Setup
- For OpenAI models: Set `OPENAI_API_KEY` environment variable
- For local GPT-OSS models: Install Ollama, pull `gpt-oss:20b` model, and run `ollama serve`

## Architecture

This is a Gradio-based web application for webpage summarization with the following key components:

### Core Classes
- **WebSite**: Data structure holding webpage content (url, title, body, links)
- **WebUrlCrawler**: Handles web scraping using BeautifulSoup with request headers and content cleaning
- **LLMClient**: Unified interface for both OpenAI API and local Ollama models

### Application Flow
1. User inputs URL via Gradio interface
2. WebUrlCrawler extracts webpage content and removes irrelevant elements (scripts, styles, images)
3. LLMClient generates summary using either OpenAI GPT-4o-mini or local GPT-OSS:20b model
4. Summary returned as markdown with TL;DR section

### Model Integration
- OpenAI models use standard OpenAI client
- Local models connect to Ollama server at `http://localhost:11434/v1`
- Single `generate_text` method abstracts model differences

### Interface Design
- Gradio Blocks layout with URL input, model selection radio buttons
- Markdown output component for formatted summaries
- Pre-configured examples for testing