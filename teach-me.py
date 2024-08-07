import subprocess
import sys
import datetime

def log(message):
    timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    print(f"[{timestamp}] {message}")

def run_subprocess(command):
    process = subprocess.Popen(command, stdout=subprocess.PIPE, stderr=subprocess.STDOUT, text=True, bufsize=1)
    while True:
        output = process.stdout.readline()
        if output == '' and process.poll() is not None:
            break
        if output:
            print(output.strip(), flush=True)
    return process.poll()

log("Starting daily-run.py")

# Loop random_pdf_reader with ./pdfs 20 as parameters
log("Starting random_pdf_reader loop...")
loop_count = 0
while True:
    try:
        loop_count += 1
        log(f"Running random_pdf_reader (iteration {loop_count})...")
        return_code = run_subprocess(["python", "random_pdf_reader.py", "./pdfs", "20"])
        log(f"random_pdf_reader completed with return code: {return_code}")
    except KeyboardInterrupt:
        log("Script terminated by user.")
        break
    except Exception as e:
        log(f"Error running random_pdf_reader: {e}")
        log("Continuing to next iteration...")

log("daily-run.py completed")
