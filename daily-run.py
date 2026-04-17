#!/usr/bin/env python3
import subprocess
import sys
import datetime
import os

REPO_ROOT = os.path.dirname(os.path.abspath(__file__))
NEWS_SCRIPT = os.path.join(REPO_ROOT, "news", "ai-news.py")
PDF_READER_SCRIPT = os.path.join(REPO_ROOT, "readers", "random_pdf_reader.py")


def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")


def run_subprocess(command, cwd=None):
    process = subprocess.Popen(
        command, cwd=cwd, stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
        text=True, bufsize=1,
    )
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip(), flush=True)
    return process.poll()


if __name__ == "__main__":
    log("Starting daily-run.py")

    # Run news/ai-news.py once (from the news/ directory so relative paths work)
    log("Attempting to run ai-news.py...")
    try:
        return_code = run_subprocess(["python", NEWS_SCRIPT], cwd=os.path.dirname(NEWS_SCRIPT))
        log(f"ai-news.py completed with return code: {return_code}")
    except Exception as e:
        log(f"Error running ai-news.py: {e}")

    # Loop random_pdf_reader with ./pdfs 20 as parameters
    log("Starting random_pdf_reader loop...")
    loop_count = 0
    while True:
        try:
            loop_count += 1
            log(f"Running random_pdf_reader (iteration {loop_count})...")
            return_code = run_subprocess(
                ["python", PDF_READER_SCRIPT, "./pdfs", "20"],
                cwd=REPO_ROOT,
            )
            log(f"random_pdf_reader completed with return code: {return_code}")
        except KeyboardInterrupt:
            log("Script terminated by user.")
            break
        except Exception as e:
            log(f"Error running random_pdf_reader: {e}")
            log("Continuing to next iteration...")

    log("daily-run.py completed")
