import os
import argparse
from Lib import text_split
import shutil

def clear_output_directory(output_dir):
    if os.path.exists(output_dir):
        shutil.rmtree(output_dir)
    os.makedirs(output_dir)

def split_file(input_file, output_dir, max_chars=4000):
    clear_output_directory(output_dir)

    file_content = text_split.read_text_file(input_file)

    chunks = text_split.split_by_sentences(file_content, max_chars)

    for i, chunk in enumerate(chunks, start=1):
        visible_char_count = sum(1 for c in chunk if c.isprintable() or c.isspace())
        print(f"Chunk {i}: {visible_char_count} visible characters")
        output_file = os.path.join(output_dir, f"part_{i:03d}.txt")
        with open(output_file, 'w', encoding='utf-8', newline='') as file:
            file.write(chunk)

    print(f"Die Datei wurde in {len(chunks)} Teile aufgeteilt.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Teilt eine Textdatei in kleinere Chunks auf.")
    parser.add_argument("input_file", help="Pfad zur Eingabedatei")
    parser.add_argument("output_dir", help="Pfad zum Ausgabeordner")
    parser.add_argument("-c", "--chunk_size", type=int, default=4000, help="Maximale Anzahl der Zeichen pro Chunk (Standard: 4000)")

    args = parser.parse_args()

    split_file(args.input_file, args.output_dir, args.chunk_size)