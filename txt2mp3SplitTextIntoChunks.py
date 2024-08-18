import os
import re
import argparse

def split_file(input_file, output_dir, max_chars=4000, num_chunks=None, debug=False):
    os.makedirs(output_dir, exist_ok=True)

    with open(input_file, 'r', encoding='utf-8') as file:
        content = file.read()

    sentences = re.split(r'(?<=[.!?])\s+', content)
    chunks = []
    current_chunk = ""

    for sentence in sentences:
        if debug:
            print(f"\nAktueller Satz: {sentence}")
            input("Drücken Sie Enter, um fortzufahren...")

        if not current_chunk and len(sentence) > max_chars:
            # Wortweises Splitten für sehr lange Sätze
            words = sentence.split()
            for word in words:
                if len(current_chunk) + len(word) + 1 <= max_chars:
                    current_chunk += word + " "
                else:
                    chunks.append(current_chunk.strip())
                    current_chunk = word + " "
            continue

        if len(current_chunk) + len(sentence) + 1 <= max_chars:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

        if debug:
            print(f"Aktueller Chunk: {current_chunk}")
            print(f"Anzahl der Chunks: {len(chunks)}")

    if current_chunk:
        chunks.append(current_chunk.strip())

    # Wenn num_chunks angegeben ist, passe die Chunks entsprechend an
    if num_chunks and num_chunks < len(chunks):
        new_chunks = []
        chunk_size = len(chunks) // num_chunks
        remainder = len(chunks) % num_chunks

        start = 0
        for i in range(num_chunks):
            end = start + chunk_size + (1 if i < remainder else 0)
            new_chunks.append(" ".join(chunks[start:end]))
            start = end

        chunks = new_chunks

    for i, chunk in enumerate(chunks, start=1):
        output_file = os.path.join(output_dir, f"part_{i:03d}.txt")
        with open(output_file, 'w', encoding='utf-8') as file:
            file.write(chunk)

    print(f"Die Datei wurde in {len(chunks)} Teile aufgeteilt.")

if __name__ == "__main__":
    parser = argparse.ArgumentParser(description="Teilt eine Textdatei in kleinere Chunks auf.")
    parser.add_argument("input_file", help="Pfad zur Eingabedatei")
    parser.add_argument("output_dir", help="Pfad zum Ausgabeordner")
    parser.add_argument("-c", "--chunk_size", type=int, default=4000, help="Maximale Anzahl der Zeichen pro Chunk (Standard: 4000)")
    parser.add_argument("-n", "--num_chunks", type=int, help="Ungefähre Anzahl der zu erstellenden Chunks (optional)")
    parser.add_argument("-d", "--debug", action="store_true", help="Aktiviert den Debug-Modus")

    args = parser.parse_args()

    split_file(args.input_file, args.output_dir, args.chunk_size, args.num_chunks, args.debug)