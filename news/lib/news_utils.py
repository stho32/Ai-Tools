#!/usr/bin/env python3
import os
import json
import requests
from bs4 import BeautifulSoup
import anthropic
import hashlib
import time

from openai import OpenAI
openai_client = OpenAI(api_key=os.environ.get("OPENAI_API_KEY"))

anthropic_client = anthropic.Anthropic(api_key=os.environ.get("ANTHROPIC_API_KEY"))


def call_gpt(system_message, user_message):
    config = load_config()
    model_config = config.get('model_config', {'provider': 'openai', 'model': 'gpt-4'})
    provider = model_config.get('provider', 'openai')
    model = model_config.get('model', 'gpt-4')

    print(f"[DEBUG] Calling {provider} API with model {model}")
    try:
        if provider == 'openai':
            response = openai_client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": system_message},
                    {"role": "user", "content": user_message}
                ]
            )
            return response.choices[0].message.content
        elif provider == 'anthropic':
            response = anthropic_client.messages.create(
                model=model,
                max_tokens=4096,
                system=system_message,
                messages=[
                    {
                        "role": "user",
                        "content": user_message
                    }
                ]
            )
            return response.content[0].text
        else:
            raise ValueError(f"Unsupported provider: {provider}")
    except Exception as e:
        print(f"[ERROR] Error calling {provider} API: {str(e)}")
        return None


def get_website_content(url):
    print(f"[DEBUG] Attempting to fetch content from {url}")
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64; rv:123.0) Gecko/20100101 Firefox/123.0',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8',
        'Accept-Language': 'en-US,en;q=0.5',
        'DNT': '1',
        'Connection': 'keep-alive',
        'Upgrade-Insecure-Requests': '1',
        'Sec-Fetch-Dest': 'document',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'none',
        'Sec-Fetch-User': '?1'
    }
    try:
        response = requests.get(url, headers=headers, timeout=30)
        if response.status_code != 200:
            error_msg = f"HTTP {response.status_code}"
            print(f"[DEBUG] Error fetching the website {url}: {error_msg}")
            return None, error_msg
        print(f"[DEBUG] Successfully fetched content from {url}")
        return response.text, None
    except requests.RequestException as e:
        error_msg = str(e)
        print(f"[DEBUG] Error fetching the website {url}: {error_msg}")
        return None, error_msg


def clean_html(html_content):
    print("[DEBUG] Cleaning HTML content")
    soup = BeautifulSoup(html_content, 'html.parser')

    for script in soup(["script", "style"]):
        script.decompose()

    text = soup.get_text()

    lines = (line.strip() for line in text.splitlines())
    chunks = (phrase.strip() for line in lines for phrase in line.split("  "))
    text = '\n'.join(chunk for chunk in chunks if chunk)

    print("[DEBUG] HTML content cleaned")
    return text


def hash_content(content):
    return hashlib.md5(content.encode()).hexdigest()


def get_state_directory():
    status_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), '.ai-news-status')
    os.makedirs(status_dir, exist_ok=True)
    return status_dir


def get_state_filename(url):
    return os.path.join(get_state_directory(), f"state_{hash_content(url)}.json")


def load_previous_content(url):
    filename = get_state_filename(url)
    try:
        with open(filename, 'r') as f:
            return json.load(f)
    except FileNotFoundError:
        return {"content": "", "last_processed": None}


def save_current_content(url, content):
    filename = get_state_filename(url)
    state = {
        "content": content,
        "last_processed": time.time()
    }
    with open(filename, 'w', newline='\n') as f:
        json.dump(state, f, indent=2)


def get_content_diff(previous_content, current_content):
    """
    Identifies new content by comparing current with previous content.
    Optimized for finding new/modified content only, ignoring deletions.
    Uses sets for efficient comparison and handles similar content as new.
    """
    if not previous_content:
        return current_content

    previous_lines = set(previous_content.split('\n'))
    current_lines = current_content.split('\n')

    new_content = []

    for line in current_lines:
        line = line.strip()
        if not line:
            continue
        if line not in previous_lines:
            new_content.append(line)

    return '\n'.join(new_content) if new_content else ""


def load_config(config_path=None):
    """
    Load configuration from file.
    Args:
        config_path: Path to the config file. If None, uses default ai-news-config.json
    Returns:
        dict: Configuration dictionary with default values if loading fails
    """
    base_dir = os.path.dirname(os.path.dirname(__file__))

    if config_path is None:
        config_path = os.path.join(base_dir, 'ai-news-config.json')
    elif not os.path.isabs(config_path):
        config_path = os.path.join(base_dir, config_path)

    try:
        with open(config_path, 'r', encoding='utf-8') as f:
            config = json.load(f)
            if 'categories' not in config:
                config['categories'] = {}
            if 'news_sources' not in config:
                config['news_sources'] = []
            if 'output_prefix' not in config:
                config['output_prefix'] = 'tech_news'
            return config
    except Exception as e:
        print(f"[ERROR] Failed to load configuration from {config_path}: {str(e)}")
        print("[INFO] Using example config as fallback")

        example_path = os.path.join(base_dir, 'ai-news-config.example.json')
        try:
            with open(example_path, 'r', encoding='utf-8') as f:
                config = json.load(f)
                config['output_prefix'] = 'tech_news'
                return config
        except Exception as e2:
            print(f"[ERROR] Failed to load example config: {str(e2)}")

        return {
            "categories": {},
            "news_sources": [],
            "output_prefix": "tech_news"
        }


def get_gpt4_analysis(content, url, keywords, category):
    print(f"[DEBUG] Starting GPT-4 analysis for {url} in category {category}")
    keywords_str = ", ".join(keywords)

    config = load_config()
    categories = config.get('categories', {})
    category_config = categories.get(category, {})
    system_message = category_config.get('system_message', "You are an expert technology analyst.")

    user_message = """Please analyze the following new content from {0} and provide a summary of the latest developments related to {1},
    focusing on these keywords: {2}. Highlight the most important updates and their practical implications for developers.
    Provide the summary in German.

    Content to analyze:
    {3}
    """.format(url, category, keywords_str, content)

    return call_gpt(system_message, user_message)
