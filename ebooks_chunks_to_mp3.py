import os
import argparse
from Lib.pdf_audio_tools import chunk_to_speech
from pydub import AudioSegment

def chunks_to_mp3(output_dir):
    for filename in sorted(os.listdir(output_dir)):
        if filename.endswith('.txt'):
            mp3_filename = os.path.splitext(filename)[0] + '.mp3'
            mp3_path = os.path.join(output_dir, mp3_filename)
            
            if not os.path.exists(mp3_path):
                chunk_path = os.path.join(output_dir, filename)
                with open(chunk_path, 'r', encoding='utf-8') as file:
                    chunk_text = file.read()

                print(f"Converting {filename} to MP3...")
                audio_contents = chunk_to_speech(chunk_text)
                
                # Save the audio file
                with open(mp3_path, 'wb') as f:
                    f.write(audio_contents)

    combined = AudioSegment.empty()
    for filename in sorted(os.listdir(output_dir)):
        if filename.endswith('.mp3'):
            mp3_path = os.path.join(output_dir, filename)
            audio = AudioSegment.from_mp3(mp3_path)
            combined += audio

    # Export the final combined MP3
    final_mp3_path = os.path.join(output_dir, "final_audio.mp3")
    combined.export(final_mp3_path, format="mp3")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Convert text chunks to MP3 files and combine them.")
    parser.add_argument("output_dir", help="Path to the directory containing text chunks")

    args = parser.parse_args()

    chunks_to_mp3(args.output_dir)