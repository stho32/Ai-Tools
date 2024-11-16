import time
import sys
import os
from Lib.pdf_audio_tools import (
    get_website_content,
    clean_html,
    load_previous_content,
    save_current_content,
    get_content_diff,
    call_gpt,
    text_to_speech,
    play_audio
)

# Configuration for URLs and keywords
NEWS_SOURCES = [
    {"url": "https://www.cursor.com/blog", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://changelog.cursor.sh/", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://aider.chat/blog/", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://big-agi.com/blog", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://www.builder.io/", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]},
    {"url": "https://codesubmit.io/blog/ai-code-tools", "keywords": ["AI", "Artificial Intelligence", "Machine Learning", "Deep Learning", "NLP"]}
]

def get_gpt4_analysis(content, url, keywords):
    print(f"[DEBUG] Starting GPT-4 analysis for {url}")
    keywords_str = ", ".join(keywords)
    system_message = "You are an AI assistant capable of analyzing web content and extracting relevant information about artificial intelligence."
    user_message = f"Please analyze the following new content from {url} and provide a summary of the latest news and developments related to artificial intelligence, focusing on these keywords: {keywords_str}. Highlight the most recent and important AI developments. Here's the new content:\n\n{content}"
    return call_gpt(system_message, user_message)

def process_source(source):
    url = source["url"]
    keywords = source["keywords"]
    print(f"[DEBUG] Processing source: {url}")
    
    previous_state = load_previous_content(url)
    previous_content = previous_state["content"]
    
    html_content = get_website_content(url)
    if html_content:
        print(f"[DEBUG] Content fetched for {url}, cleaning HTML")
        cleaned_content = clean_html(html_content)
        
        new_content = get_content_diff(previous_content, cleaned_content)
        
        if new_content.strip():  # Check if there's any non-whitespace content
            print(f"[DEBUG] New content found, starting analysis")
            analysis = get_gpt4_analysis(new_content, url, keywords)
            if analysis:
                print(f"[DEBUG] Analysis completed for {url}")
                print("\nAnalysis:")
                print(analysis)
                
                print("\n[DEBUG] Starting text-to-speech conversion")
                audio_contents = text_to_speech(analysis)
                if audio_contents:
                    print("[DEBUG] Text-to-speech conversion successful, saving audio")
                    output_filename = f"ai_news_{int(time.time())}.mp3"
                    audio_path = play_audio(audio_contents, output_filename)
                    if audio_path:
                        print(f"[INFO] Audio saved as: {audio_path}")
                        # You can add code here to play the audio file if desired
                    else:
                        print("[ERROR] Failed to save audio")
                else:
                    print("[DEBUG] Failed to convert text to speech")
            else:
                print(f"[DEBUG] Failed to generate an analysis for {url}")
        else:
            print(f"[DEBUG] No new content found for {url}")
        
        save_current_content(url, cleaned_content)
    else:
        print(f"[DEBUG] Failed to fetch the content from {url}")

def main():
    print("[DEBUG] Starting main function")
    
    for i, source in enumerate(NEWS_SOURCES, 1):
        print(f"\n[DEBUG] Processing source {i} of {len(NEWS_SOURCES)}")
        process_source(source)
        
        if i < len(NEWS_SOURCES):
            print("\n[DEBUG] Waiting before processing next source")
            time.sleep(5)  # Wait 5 seconds before processing the next source
    
    print("[DEBUG] All sources processed")

if __name__ == "__main__":
    print("[DEBUG] Script started")
    main()
    print("[DEBUG] Script completed")