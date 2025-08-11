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
- Set `OPENAI_API_KEY` environment variable

## Architecture

This is a Gradio-based web application for webpage summarization with the following key components:

### Core Classes
- **WebSite**: Data structure holding webpage content (url, title, body, links)
- **WebUrlCrawler**: Handles web scraping using BeautifulSoup with request headers and content cleaning
- **LLMClient**: Interface for OpenAI API integration

### Application Flow
1. User inputs URL via Gradio interface
2. WebUrlCrawler extracts webpage content and removes irrelevant elements (scripts, styles, images)
3. LLMClient generates summary using OpenAI GPT-4o-mini model
4. Summary returned as markdown with TL;DR section

### Model Integration
- Uses standard OpenAI client
- Single `generate_text` method for API communication

### Interface Design
- Gradio Blocks layout with URL input
- Markdown output component for formatted summaries
- Pre-configured examples for testing