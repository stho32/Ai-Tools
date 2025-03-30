# MD to MP3 Pro

A Python tool that converts Markdown files to MP3 audio files using OpenAI's text-to-speech API.

## Features

- Tracks file changes using SHA-256 hashing
- Only processes modified or new files
- **Resumes processing automatically after interruption or crashes**
- Uses OpenAI's text-to-speech API with varied voices and speaking styles
- Processes files in parallel for faster conversion
- Stores audio files alongside markdown files
- Supports a working directory for caching and temporary files
- Fallback mechanism if the preferred TTS model is unavailable

## Requirements

- Python 3.8+
- An OpenAI API key with access to TTS models
- Required Python packages:
  - openai
  - pydub
  - pathlib
  - asyncio

## Installation

1. Clone or download this repository
2. Set up your OpenAI API key as an environment variable:

```bash
# On Windows
set OPENAI_API_KEY=your_api_key_here

# On macOS/Linux
export OPENAI_API_KEY=your_api_key_here
```

3. Install the required packages:

```bash
pip install openai pydub
```

## Usage

```bash
python md_to_mp3_pro.py input_path work_path [--api-key API_KEY]
```

### Parameters

- `input_path`: Directory containing markdown files
- `work_path`: Working directory for temporary files and hash memory
- `--api-key` (optional): Your OpenAI API key if not set as environment variable

### Example

```bash
python md_to_mp3_pro.py C:\Projekte\Seminar-Prozess\Seminar-Prozess C:\Projekte\Seminar-Prozess-Arbeitspfad
```

## How It Works

1. The tool scans the input directory for all markdown (`.md`) files
2. It calculates a SHA-256 hash for each file and compares it with stored hashes
3. For new, modified, or previously interrupted files:
   - The tool marks each file as "processing" before starting
   - The markdown content is split into manageable chunks
   - Each chunk is sent to OpenAI's text-to-speech API
   - For each chunk, a random voice and speaking style is used
   - The resulting audio segments are combined into a single MP3 file
   - The MP3 file is saved with the same name as the markdown file but with `.mp3` extension
   - Upon successful completion, the file is marked as "completed"
4. If processing is interrupted (e.g., due to crash or manual termination):
   - The next time the tool runs, it will detect previously interrupted files
   - Processing will resume for all files that didn't complete successfully
5. The updated file hashes and status information are stored in the work directory

## Interruption Handling

The tool is designed to be resilient to interruptions:

- If the program crashes or is terminated during execution, the next run will automatically resume processing
- Files that were being processed during interruption will be detected and reprocessed
- Completed files will not be reprocessed unless their content changes
- Progress tracking ensures that you can safely stop and restart the tool at any time

## Voice Styles

The tool includes 10 different voice styles:
- Energetic Instructor
- Academic Professor
- Friendly Mentor
- Practical Coach
- Storyteller
- Mysterious Narrator
- Energetic Host
- Horror Storyteller
- Gentle Guide
- Technical Expert

For each text chunk, a random voice style and OpenAI voice is selected to create varied and engaging audio.

## Working Directory Structure

The working directory contains:
- `file_hashes.json`: Stored hashes and processing status of files
- Temporary directories for each processed file containing:
  - Temporary audio chunks before combining
  - Other temporary processing files

## Troubleshooting

- **API Key Issues**: Ensure your OpenAI API key is correctly set as an environment variable or passed via the `--api-key` parameter
- **Model Unavailable**: The tool will automatically try fallback models if the preferred model is unavailable
- **File Encoding**: Ensure your markdown files are UTF-8 encoded to avoid character issues
- **Large Files**: Very large markdown files might take considerable time to process

## License

This tool is provided as-is for personal and educational use.
