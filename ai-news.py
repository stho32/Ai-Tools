import time
import sys
import os
from datetime import datetime
from Lib.pdf_audio_tools import (
    get_website_content,
    clean_html,
    load_previous_content,
    save_current_content,
    get_content_diff,
    call_gpt
)

# Configuration for URLs and keywords
NEWS_SOURCES = [
    # DotNet
    #{"url": "https://devblogs.microsoft.com/dotnet/category/csharp/", "keywords": ["C#", ".NET", "ASP.NET", "Performance", "Features"], "category": "DotNet"},
    #{"url": "https://www.hanselman.com/blog/", "keywords": ["C#", ".NET", "ASP.NET", "Development", "Microsoft"], "category": "DotNet"},
    #{"url": "https://devblogs.microsoft.com/visualstudio/", "keywords": ["Visual Studio", "Development", "Tools", "Features"], "category": "DotNet"},
    #{"url": "https://devblogs.microsoft.com/aspnet/", "keywords": ["ASP.NET", "Web Development", "Performance", "Security"], "category": "DotNet"},
    #{"url": "https://www.dotnetconf.net/", "keywords": [".NET Conf", "Conference", "Announcements", "Features"], "category": "DotNet"},

    # HTML
    #{"url": "https://developer.mozilla.org/blog/", "keywords": ["HTML", "Web Standards", "Browser", "Features"], "category": "HTML"},
    #{"url": "https://www.w3.org/blog/", "keywords": ["Web Standards", "HTML", "Specifications", "Working Groups"], "category": "HTML"},
    #{"url": "https://web.dev/blog", "keywords": ["Web Development", "Best Practices", "Performance", "Standards"], "category": "HTML"},
    #{"url": "https://blog.whatwg.org/", "keywords": ["HTML Living Standard", "Web Standards", "Browser"], "category": "HTML"},
    #{"url": "https://www.smashingmagazine.com/", "keywords": ["Web Development", "Design", "HTML", "Best Practices"], "category": "HTML"},

    # JavaScript
    #{"url": "https://javascriptweekly.com/", "keywords": ["JavaScript", "ECMAScript", "Node.js", "Frameworks"], "category": "JavaScript"},
    #{"url": "https://v8.dev/blog", "keywords": ["V8 Engine", "Performance", "JavaScript", "Features"], "category": "JavaScript"},
    #{"url": "https://2ality.com/", "keywords": ["JavaScript", "ECMAScript", "Features", "Development"], "category": "JavaScript"},
    #{"url": "https://tc39.es/", "keywords": ["ECMAScript", "JavaScript", "Standards", "Proposals"], "category": "JavaScript"},
    #{"url": "https://javascript.info/", "keywords": ["JavaScript", "Tutorials", "Best Practices", "Features"], "category": "JavaScript"},
    #{"url": "https://nodejs.org/en/blog/", "keywords": ["Node.js", "JavaScript", "Runtime", "Updates"], "category": "JavaScript"},
    #{"url": "https://stateofjs.com/", "keywords": ["JavaScript", "Frameworks", "Tools", "Trends"], "category": "JavaScript"},

    # CSS
    #{"url": "https://css-tricks.com/", "keywords": ["CSS", "Web Design", "Layouts", "Features"], "category": "CSS"},
    #{"url": "https://www.w3.org/blog/CSS/", "keywords": ["CSS", "Standards", "Specifications", "Features"], "category": "CSS"},
    #{"url": "https://developer.chrome.com/blog/", "keywords": ["Chrome", "Web Platform", "CSS", "Features"], "category": "CSS"},
    #{"url": "https://www.joshwcomeau.com/", "keywords": ["CSS", "Web Design", "Animations", "Tutorials"], "category": "CSS"},
    #{"url": "https://css-weekly.com/", "keywords": ["CSS", "Web Design", "News", "Techniques"], "category": "CSS"},

    # Microsoft SQL Server
    #{"url": "https://www.microsoft.com/en-us/sql-server/blog/", "keywords": ["SQL Server", "Database", "Performance", "Features"], "category": "SQL"},
    #{"url": "https://techcommunity.microsoft.com/t5/sql-server-blog/bg-p/SQLServer", "keywords": ["SQL Server", "Updates", "Best Practices", "Features"], "category": "SQL"},
    #{"url": "https://learn.microsoft.com/en-us/sql/sql-server/", "keywords": ["SQL Server", "Documentation", "Updates", "Features"], "category": "SQL"},
    #{"url": "https://www.brentozar.com/blog/", "keywords": ["SQL Server", "Performance", "Tuning", "Best Practices"], "category": "SQL"},
    #{"url": "https://www.sqlservercentral.com/", "keywords": ["SQL Server", "Tips", "Tutorials", "Community"], "category": "SQL"},

    # PowerShell
    #{"url": "https://devblogs.microsoft.com/powershell/", "keywords": ["PowerShell", "Scripting", "Automation", "Features"], "category": "PowerShell"},
    #{"url": "https://devblogs.microsoft.com/powershell-community/", "keywords": ["PowerShell", "Community", "Scripts", "Tips"], "category": "PowerShell"},
    #{"url": "https://jdhitsolutions.com/blog/", "keywords": ["PowerShell", "Scripting", "Tips", "Tutorials"], "category": "PowerShell"},
    #{"url": "https://donjones.com/", "keywords": ["PowerShell", "Automation", "Best Practices", "Training"], "category": "PowerShell"},
    #{"url": "https://powershellexplained.com/", "keywords": ["PowerShell", "Tutorials", "Examples", "Tips"], "category": "PowerShell"},

    # Blazor
    #{"url": "https://devblogs.microsoft.com/dotnet/category/blazor/", "keywords": ["Blazor", "Web Development", "WebAssembly", "Features"], "category": "Blazor"},
    #{"url": "https://blog.stevensanderson.com/", "keywords": ["Blazor", "WebAssembly", "Development", "Tips"], "category": "Blazor"},
    #{"url": "https://blazor-university.com/", "keywords": ["Blazor", "Tutorials", "Components", "Best Practices"], "category": "Blazor"},
    #{"url": "https://chrissainty.com/", "keywords": ["Blazor", "Development", "Components", "Tips"], "category": "Blazor"},
    #{"url": "https://blazortrain.com/", "keywords": ["Blazor", "Training", "Tutorials", "Development"], "category": "Blazor"},

    # AI
    {"url": "https://openai.com/news/", "keywords": ["AI", "GPT", "Machine Learning", "Research"], "category": "AI"},
    {"url": "https://www.anthropic.com/news/", "keywords": ["AI", "Claude", "Machine Learning", "Safety"], "category": "AI"},
    {"url": "https://blog.google/products/gemini/", "keywords": ["Gemini", "AI", "Machine Learning", "Google"], "category": "AI"},
    {"url": "https://www.cursor.com/blog", "keywords": ["AI", "Development Tools", "Coding", "Features"], "category": "AI"},
    {"url": "https://changelog.cursor.sh/", "keywords": ["Cursor", "AI", "Development", "Updates"], "category": "AI"},
    {"url": "https://aider.chat/blog/", "keywords": ["AI", "Coding Assistant", "Development", "Features"], "category": "AI"},
    {"url": "https://codesubmit.io/blog/ai-code-tools", "keywords": ["AI", "Code Tools", "Development", "Reviews"], "category": "AI"},
    {"url": "https://www.heise.de/", "keywords": ["AI", "Technology", "News", "German"], "category": "AI"},
    {"url": "https://techcrunch.com/category/artificial-intelligence/", "keywords": ["AI", "Startups", "Technology", "Industry"], "category": "AI"}
]

def get_gpt4_analysis(content, url, keywords, category):
    print(f"[DEBUG] Starting GPT-4 analysis for {url} in category {category}")
    keywords_str = ", ".join(keywords)
    
    system_messages = {
        "DotNet": "You are an expert .NET developer who analyzes news and updates in the .NET ecosystem.",
        "HTML": "You are a web standards expert who analyzes developments in HTML and web technologies.",
        "JavaScript": "You are a JavaScript expert who analyzes developments in the JavaScript ecosystem.",
        "CSS": "You are a CSS expert who analyzes developments in web styling and design.",
        "SQL": "You are a SQL Server expert who analyzes developments in database technologies.",
        "PowerShell": "You are a PowerShell expert who analyzes developments in automation and scripting.",
        "Blazor": "You are a Blazor expert who analyzes developments in web development with WebAssembly.",
        "AI": "You are an AI expert who analyzes developments in artificial intelligence and machine learning."
    }
    
    system_message = system_messages.get(category, "You are an expert technology analyst.")
    user_message = """Please analyze the following new content from {0} and provide a summary of the latest developments related to {1}, 
    focusing on these keywords: {2}. Highlight the most important updates and their practical implications for developers.
    Please respond in German. Here's the new content:\n\n{3}""".format(
        url,
        category,
        keywords_str,
        content
    )
    
    return call_gpt(system_message, user_message)

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

    category_icons = {
        "DotNet": "bi-code-square",
        "HTML": "bi-file-earmark-code",
        "JavaScript": "bi-filetype-js",
        "CSS": "bi-palette",
        "SQL": "bi-database",
        "PowerShell": "bi-terminal",
        "Blazor": "bi-lightning",
        "AI": "bi-robot"
    }

    category_colors = {
        "DotNet": "primary",
        "HTML": "warning",
        "JavaScript": "warning",
        "CSS": "info",
        "SQL": "success",
        "PowerShell": "dark",
        "Blazor": "danger",
        "AI": "secondary"
    }

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
        nav_items.append(
            '<a class="flex-sm-fill text-sm-center nav-link" href="#{0}">'
            '<i class="bi {1}"></i> {0}'
            '</a>'.format(
                category,
                category_icons.get(category, "bi-bookmark")
            )
        )
    category_nav = "\n".join(nav_items)

    # Generate content
    content_sections = []
    for category in sorted(categorized_results.keys()):
        items = categorized_results[category]
        category_content = []
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
            category_icons.get(category, 'bi-bookmark'),
            category_colors.get(category, 'secondary'),
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

def main():
    print("[DEBUG] Starting main function")
    timestamp = time.time()
    results = []
    
    for i, source in enumerate(NEWS_SOURCES, 1):
        print(f"\n[DEBUG] Processing source {i} of {len(NEWS_SOURCES)}")
        result = process_source(source)
        results.append(result)
    
    # Generate HTML report
    print("\n[DEBUG] Generating HTML report")
    html_content = generate_html_report(results, timestamp)
    
    # Save HTML report
    report_filename = os.path.abspath(f"tech_news_{int(timestamp)}.html")
    with open(report_filename, "w", encoding="utf-8") as f:
        f.write(html_content)
    
    print(f"[DEBUG] Report saved as {report_filename}")
    
    # Open the HTML file in the default browser
    print("[DEBUG] Opening report in default browser")
    os.startfile(report_filename)
    
    print("[DEBUG] All sources processed")

if __name__ == "__main__":
    print("[DEBUG] Script started")
    main()
    print("[DEBUG] Script completed")