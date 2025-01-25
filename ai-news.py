import os
import time
import json
import argparse
from datetime import datetime
from Lib.pdf_audio_tools import (
    get_website_content,
    clean_html,
    get_gpt4_analysis,
    load_previous_content,
    save_current_content,
    get_content_diff,
    call_gpt,
    load_config
)

def process_source(source):
    url = source["url"]
    keywords = source["keywords"]
    category = source["category"]
    result = {
        "url": url,
        "keywords": keywords,
        "category": category,
        "analysis": None,
        "error": None
    }
    
    print(f"[DEBUG] Processing source: {url}")
    
    try:
        previous_state = load_previous_content(url)
        previous_content = previous_state["content"]
        
        html_content, error = get_website_content(url)
        if html_content:
            print(f"[DEBUG] Content fetched for {url}, cleaning HTML")
            cleaned_content = clean_html(html_content)
            
            new_content = get_content_diff(previous_content, cleaned_content)
            
            if new_content.strip():  # Check if there's any non-whitespace content
                print(f"[DEBUG] New content found, starting analysis")
                analysis = get_gpt4_analysis(new_content, url, keywords, category)
                if analysis:
                    print(f"[DEBUG] Analysis completed for {url}")
                    result["analysis"] = analysis
                else:
                    result["error"] = "Failed to generate analysis"
            else:
                result["error"] = "No new content found"
            
            save_current_content(url, cleaned_content)
        else:
            result["error"] = error or "Failed to fetch content"
    except Exception as e:
        result["error"] = str(e)
        print(f"[ERROR] Error processing {url}: {str(e)}")
    
    return result

def generate_html_report(results, timestamp):
    html_template = """
<!DOCTYPE html>
<html lang="de">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Tech News Update - {date}</title>
    <link href="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/css/bootstrap.min.css" rel="stylesheet">
    <link rel="stylesheet" href="https://cdn.jsdelivr.net/npm/bootstrap-icons@1.11.3/font/bootstrap-icons.css">
    <style>
        .category-section {{ margin-bottom: 2rem; }}
        .news-card {{ margin-bottom: 1rem; }}
        .source-link {{ text-decoration: none; }}
        .source-link:hover {{ text-decoration: underline; }}
        .news-meta {{ font-size: 0.9rem; color: #666; }}
        .category-icon {{ margin-right: 0.5rem; }}
        body {{ padding-top: 2rem; }}
        .category-header {{
            background: #f8f9fa;
            padding: 1rem;
            margin-bottom: 1.5rem;
            border-radius: 0.5rem;
        }}
        .category-badge {{
            font-size: 1rem;
            padding: 0.5rem 1rem;
            margin-bottom: 1rem;
        }}
        .error-text {{
            color: #dc3545;
            font-style: italic;
        }}
    </style>
</head>
<body>
    <div class="container">
        <header class="text-center mb-5">
            <h1 class="display-4">Tech News Update</h1>
            <p class="lead text-muted">{date}</p>
        </header>

        <div class="row">
            <div class="col-12">
                <nav class="nav nav-pills flex-column flex-sm-row mb-4">
                    {category_nav}
                </nav>
            </div>
        </div>

        {content}

        <footer class="text-center mt-5 mb-5 text-muted">
            <p>Generated on {datetime}</p>
        </footer>
    </div>
    <script src="https://cdn.jsdelivr.net/npm/bootstrap@5.3.2/dist/js/bootstrap.bundle.min.js"></script>
</body>
</html>
"""

    config = load_config()
    categories = config.get('categories', {})

    # Group results by category
    categorized_results = {}
    for result in results:
        category = result["category"]
        if category not in categorized_results:
            categorized_results[category] = []
        categorized_results[category].append(result)

    # Generate navigation
    nav_items = []
    for category in sorted(categorized_results.keys()):
        category_config = categories.get(category, {})
        icon = category_config.get('icon', 'bi-bookmark')
        nav_items.append(
            '<a class="flex-sm-fill text-sm-center nav-link" href="#{0}">'
            '<i class="bi {1}"></i> {0}'
            '</a>'.format(category, icon)
        )
    category_nav = "\n".join(nav_items)

    # Generate content
    content_sections = []
    for category in sorted(categorized_results.keys()):
        items = categorized_results[category]
        category_content = []
        category_config = categories.get(category, {})
        icon = category_config.get('icon', 'bi-bookmark')
        color = category_config.get('color', 'secondary')
        
        section_template = """
            <section id="{0}" class="category-section">
                <div class="category-header">
                    <h2>
                        <i class="bi {1} category-icon"></i>
                        {0}
                    </h2>
                    <span class="badge bg-{2} category-badge">
                        {3} Updates
                    </span>
                </div>
                <div class="row">
        """
        category_content.append(section_template.format(
            category,
            icon,
            color,
            len(items)
        ))

        for item in items:
            news_template = """
                <div class="col-12 news-card">
                    <div class="card">
                        <div class="card-body">
                            <h5 class="card-title">
                                <a href="{0}" class="source-link" target="_blank">
                                    {1}
                                    <i class="bi bi-box-arrow-up-right ms-1"></i>
                                </a>
                            </h5>
                            <div class="news-meta mb-3">
                                <i class="bi bi-tags"></i> {2}
                            </div>
                            <div class="card-text">
                                {3}
                            </div>
                            {4}
                        </div>
                    </div>
                </div>
            """
            
            # Get domain name for display
            domain = item['url'].split('//')[1].split('/')[0]
            
            # Format error message if present
            error_html = ''
            if item.get('error'):
                error_html = f'<div class="error-text mt-3"><i class="bi bi-exclamation-triangle"></i> {item["error"]}</div>'
            
            category_content.append(news_template.format(
                item['url'],
                domain,
                ', '.join(item['keywords']),
                item.get('analysis', '').replace('\n', '<br>') if item.get('analysis') else '',
                error_html
            ))

        category_content.append("</div></section>")
        content_sections.append("\n".join(category_content))

    content = "\n".join(content_sections)
    
    current_time = datetime.fromtimestamp(timestamp)
    date = current_time.strftime("%d.%m.%Y")
    datetime_str = current_time.strftime("%d.%m.%Y %H:%M:%S")

    return html_template.format(
        date=date,
        datetime=datetime_str,
        category_nav=category_nav,
        content=content
    )

def get_gpt4_analysis(content, url, keywords, category):
    print(f"[DEBUG] Starting GPT-4 analysis for {url} in category {category}")
    keywords_str = ", ".join(keywords)
    
    # Get system message from config
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

def main():
    # Parse command line arguments
    parser = argparse.ArgumentParser(description='AI News Generator')
    parser.add_argument('--config', '-c', 
                      help='Path to config file (default: ai-news-config.json)',
                      default='ai-news-config.json')
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
        result = process_source(source)
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