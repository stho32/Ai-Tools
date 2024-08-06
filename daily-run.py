import subprocess
import sys
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

log("Starting daily-run.py")

# Run ai-news.py once
log("Attempting to run ai-news.py...")
try:
    result = subprocess.run(["python", "ai-news.py"], capture_output=True, text=True)
    log(f"ai-news.py completed with return code: {result.returncode}")
    if result.stdout:
        log(f"ai-news.py output: {result.stdout}")
    if result.stderr:
        log(f"ai-news.py error: {result.stderr}")
except Exception as e:
    log(f"Error running ai-news.py: {e}")

# Loop random_pdf_reader with ./pdfs 20 as parameters
log("Starting random_pdf_reader loop...")
loop_count = 0
while True:
    try:
        loop_count += 1
        log(f"Running random_pdf_reader (iteration {loop_count})...")
        result = subprocess.run(["python", "random_pdf_reader.py", "./pdfs", "20"], capture_output=True, text=True)
        log(f"random_pdf_reader completed with return code: {result.returncode}")
        if result.stdout:
            log(f"random_pdf_reader output: {result.stdout}")
        if result.stderr:
            log(f"random_pdf_reader error: {result.stderr}")
    except KeyboardInterrupt:
        log("Script terminated by user.")
        break
    except Exception as e:
        log(f"Error running random_pdf_reader: {e}")
        log("Continuing to next iteration...")

log("daily-run.py completed")