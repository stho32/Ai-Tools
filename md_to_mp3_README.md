# MdBuch2MP3

This script converts a collection of markdown files into a combined MP3 audiobook using OpenAI's text-to-speech API.

## Requirements

The script requires the following packages (which are already in the requirements.txt file):
- openai >= 1.0.0
- pydub >= 0.25.1

## Installation

Ensure you have the required packages installed:

```bash
pip install -r requirements.txt
```

You'll also need to have an OpenAI API key for accessing the text-to-speech service.

## Usage

```bash
python md_to_mp3.py input_path output_path [--voice VOICE] [--model MODEL] [--api-key API_KEY]
```

### Arguments

- `input_path`: Directory containing markdown (.md) files
- `output_path`: Directory where the output MP3 and text files will be saved
- `--voice`: OpenAI TTS voice to use (default: "alloy")
- `--model`: OpenAI TTS model to use (default: "tts-1")
- `--api-key`: Your OpenAI API key (optional, can also be set via OPENAI_API_KEY environment variable)

### Example

```bash
python md_to_mp3.py C:\Books\MyBook C:\Output --voice coral --model tts-1
```

## How It Works

1. The script collects all markdown files from the input directory
2. Files are sorted alphabetically by filename
3. Each file's content is combined with the filename (without .md extension) as a heading
4. The combined text is saved as a .txt file in the output directory
5. The text is divided into chunks that can be processed by the OpenAI API
6. Each chunk is converted to speech using the OpenAI TTS API
7. All audio chunks are combined into a single MP3 file
8. The final MP3 is named after the input directory

## Available Voices

OpenAI offers several voice options:
- alloy (default)
- echo
- fable
- onyx
- nova
- shimmer
- coral

## Available Models

- tts-1 (default)
- tts-1-hd

## Notes

- The script creates temporary files during processing that are automatically cleaned up
- The API has limits on the size of text that can be processed at once, which the script handles
- Processing large books may take time and use significant API credits
