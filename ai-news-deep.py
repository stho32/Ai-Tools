import os
import time
import json
import argparse
from datetime import datetime
from urllib.parse import urljoin, urlparse
from bs4 import BeautifulSoup
import requests
from Lib.pdf_audio_tools import (
    clean_html,
    get_gpt4_analysis,
    load_previous_content,
    save_current_content,
    get_content_diff,
    call_gpt,
    load_config
)
import random

# Standard pages to exclude from crawling
EXCLUDED_PATTERNS = [
    # Legal & Company
    'impressum', 'imprint', 'privacy', 'datenschutz', 'agb', 'terms', 
    'kontakt', 'contact', 'about', 'uber-uns', 'team',
    # Navigation & Utils
    'suche', 'search', 'login', 'register', 'anmelden', 'registrieren',
    'sitemap', 'archive', 'archiv', 'feeds', 'rss',
    # Social Media
    'facebook', 'twitter', 'instagram', 'linkedin', 'youtube',
    # Shopping
    'warenkorb', 'cart', 'checkout', 'shop', 'store',
    # Account
    'profile', 'profil', 'account', 'konto', 'settings', 'einstellungen',
    # Newsletter
    'newsletter', 'subscribe', 'abonnieren',
    # Help
    'help', 'hilfe', 'faq', 'support'
]

def is_excluded_url(url):
    """Check if URL matches any excluded pattern."""
    url_lower = url.lower()
    return any(pattern in url_lower for pattern in EXCLUDED_PATTERNS)

def is_same_domain(url1, url2):
    """Check if two URLs belong to the same main domain."""
    domain1 = urlparse(url1).netloc
    domain2 = urlparse(url2).netloc
    # Remove 'www.' prefix for comparison
    domain1 = domain1.replace('www.', '')
    domain2 = domain2.replace('www.', '')
    return domain1 == domain2

def extract_links(html_content, base_url):
    """Extract all links from HTML content that belong to the same domain."""
    soup = BeautifulSoup(html_content, 'html.parser')
    links = set()  # Using set to avoid duplicates
    for a in soup.find_all('a', href=True):
        href = a.get('href')
        full_url = urljoin(base_url, href)
        if is_same_domain(base_url, full_url):
            links.add(full_url)
    return list(links)

def is_relevant_link(url, keywords):
    """Check if a URL is relevant based on keywords and not excluded."""
    if is_excluded_url(url):
        return False
    url_lower = url.lower()
    return any(keyword.lower() in url_lower for keyword in keywords)

def process_source_deep(source, max_pages=5):
    """Process a source by crawling through relevant links."""
    base_url = source["url"]
    keywords = source["keywords"]
    category = source["category"]
    
    result = {
        "url": base_url,
        "keywords": keywords,
        "category": category,
        "subpages": [],
        "error": None
    }
    
    print(f"\n[DEBUG] Processing source deeply: {base_url}")
    
    # Step 1: Get main page content
    print("[DEBUG] Fetching main page...")
    html_content, error = get_website_content(base_url)
    if error:
        result["error"] = f"Failed to fetch main page: {error}"
        return result
    
    # Step 2: Extract all links
    print("[DEBUG] Extracting all links...")
    all_links = extract_links(html_content, base_url)
    print(f"[INFO] Found {len(all_links)} total links:")
    for link in all_links:
        print(f"  - {link}")
    
    # Step 3: Filter out excluded links
    print("\n[DEBUG] Filtering out excluded links...")
    valid_links = [link for link in all_links if not is_excluded_url(link)]
    print(f"[INFO] {len(valid_links)} links remain after exclusion:")
    for link in valid_links:
        print(f"  - {link}")
    
    # Step 4: Filter for relevant links
    print("\n[DEBUG] Filtering for relevant links...")
    relevant_links = [link for link in valid_links if is_relevant_link(link, keywords)]
    print(f"[INFO] {len(relevant_links)} relevant links found:")
    for link in relevant_links:
        print(f"  - {link}")
    
    # Step 5: Randomly select max_pages links
    if len(relevant_links) > max_pages:
        print(f"\n[DEBUG] Randomly selecting {max_pages} links for processing...")
        selected_links = random.sample(relevant_links, max_pages)
    else:
        selected_links = relevant_links
    print(f"[INFO] Selected {len(selected_links)} links for processing:")
    for link in selected_links:
        print(f"  - {link}")
    
    # Step 6: Process selected links
    print("\n[DEBUG] Processing selected links...")
    for link in selected_links:
        print(f"\n[DEBUG] Processing: {link}")
        
        # Get subpage content
        subpage_html, error = get_website_content(link)
        if error:
            print(f"[WARNING] Failed to fetch subpage {link}: {error}")
            continue
        
        # Clean and analyze subpage content
        cleaned_content = clean_html(subpage_html)
        if not cleaned_content.strip():
            print(f"[WARNING] No content found in {link}")
            continue
        
        # Get previous content state
        previous_state = load_previous_content(link)
        previous_content = previous_state["content"]
        
        # Check for new content
        new_content = get_content_diff(previous_content, cleaned_content)
        if not new_content.strip():
            print(f"[INFO] No new content in {link}")
            continue
        
        # Analyze new content
        print(f"[DEBUG] Analyzing content from {link}")
        analysis = get_gpt4_analysis(new_content, link, keywords, category)
        if not analysis:
            print(f"[WARNING] Analysis failed for {link}")
            continue
        
        # Save current state
        save_current_content(link, cleaned_content)
        
        # Add to results
        result["subpages"].append({
            "url": link,
            "analysis": analysis
        })
        print(f"[INFO] Successfully processed {link}")
    
    return result

def get_website_content(url):
    """Fetch content from a URL with proper error handling."""
    try:
        headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
        response = requests.get(url, headers=headers, timeout=10)
        response.raise_for_status()
        return response.text, None
    except Exception as e:
        return None, str(e)

def generate_html_report(results, timestamp):
    """Generate HTML report for deep crawl results."""
    html_template = """
    <!DOCTYPE html>
    <html lang="de">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>News Report {date}</title>
        <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/css/bootstrap.min.css" rel="stylesheet">
        <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.7.2/font/bootstrap-icons.css">
    </head>
    <body>
        <div class="container mt-5">
            <h1 class="mb-4">News Report {date}</h1>
            {content}
        </div>
        <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.1.3/dist/js/bootstrap.bundle.min.js"></script>
    </body>
    </html>
    """
    
    content_html = ""
    for result in results:
        if result["error"]:
            continue
            
        category = result["category"]
        base_url = result["url"]
        
        # Get category styling
        config = load_config()
        category_config = config.get("categories", {}).get(category, {})
        icon = category_config.get("icon", "bi-globe")
        color = category_config.get("color", "primary")
        
        content_html += f"""
        <div class="card mb-4">
            <div class="card-header bg-{color} text-white">
                <i class="bi {icon}"></i> {category}
            </div>
            <div class="card-body">
                <h5 class="card-title">Updates von: <a href="{base_url}" target="_blank">{base_url}</a></h5>
                <div class="accordion" id="accordion_{hash(base_url)}">
        """
        
        for idx, subpage in enumerate(result["subpages"]):
            subpage_url = subpage["url"]
            analysis = subpage["analysis"]
            
            content_html += f"""
                    <div class="accordion-item">
                        <h2 class="accordion-header">
                            <button class="accordion-button {'collapsed' if idx > 0 else ''}" type="button" 
                                    data-bs-toggle="collapse" data-bs-target="#collapse_{hash(subpage_url)}">
                                {subpage_url}
                            </button>
                        </h2>
                        <div id="collapse_{hash(subpage_url)}" 
                             class="accordion-collapse collapse {'show' if idx == 0 else ''}"
                             data-bs-parent="#accordion_{hash(base_url)}">
                            <div class="accordion-body">
                                {analysis}
                            </div>
                        </div>
                    </div>
            """
        
        content_html += """
                </div>
            </div>
        </div>
        """
    
    date_str = datetime.fromtimestamp(timestamp).strftime('%d.%m.%Y %H:%M')
    return html_template.format(date=date_str, content=content_html)

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI News Generator (Deep Crawler Version)')
    parser.add_argument('--config', '-c', 
                      help='Path to config file (default: ai-news-config.json)',
                      default='ai-news-config.json')
    parser.add_argument('--max-pages', '-m',
                      help='Maximum number of subpages to process per source (default: 5)',
                      type=int, default=5)
    args = parser.parse_args()
    
    print("[DEBUG] Starting main function")
    timestamp = time.time()
    results = []
    
    # Load config from specified file
    config = load_config(args.config)
    news_sources = config.get('news_sources', [])
    output_prefix = config.get('output_prefix', 'tech_news')
    
    for i, source in enumerate(news_sources, 1):
        print(f"\n[DEBUG] Processing source {i} of {len(news_sources)}")
        result = process_source_deep(source, args.max_pages)
        results.append(result)
    
    # Generate HTML report
    print("\n[DEBUG] Generating HTML report")
    html_content = generate_html_report(results, timestamp)
    
    # Save HTML report using configured prefix
    report_filename = os.path.abspath(f"{output_prefix}_{int(timestamp)}.html")
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[DEBUG] Report saved as {report_filename}")
    
    # Open the HTML file in the default browser
    print("[DEBUG] Opening report in default browser")
    os.startfile(report_filename)
    
    print("[DEBUG] All sources processed")

if __name__ == "__main__":
    main()
