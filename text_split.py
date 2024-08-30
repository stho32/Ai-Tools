import os
import re

def read_text_file(file_path):
    with open(file_path, 'r', encoding='utf-8') as file:
        return file.read()


def split_by_characters(text, max_chars):
    chunks = []
    for i in range(0, len(text), max_chars):
        chunks.append(text[i:i+max_chars])
    return chunks

def split_by_words(text, max_chunk_size):
    chunks = []
    words = text.split()
    current_chunk = ""

    for word in words:
        if len(current_chunk) + len(word) + 1 <= max_chunk_size:
            current_chunk += word + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = word + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def split_by_sentences(text, max_chunk_size):
    chunks = []
    sentences = re.split(r'(?<=[.!?])\s+', text)
    current_chunk = ""

    for sentence in sentences:
        if len(current_chunk) + len(sentence) + 1 <= max_chunk_size:
            current_chunk += sentence + " "
        else:
            chunks.append(current_chunk.strip())
            current_chunk = sentence + " "

    if current_chunk:
        chunks.append(current_chunk.strip())

    return chunks

def test():
    data = read_text_file("C:/Projekte/Bücher-Als-Text/txt/Goldratt's Rules of Flow.txt")
    chunks = split_by_sentences(data, 4000)

    for chunk in chunks:
        if (len(chunk) > 4000):
            print("ERROR: Chunk length exceeds 4000 characters")
        print(len(chunk))


if (__name__ == "__main__"):
    test()
