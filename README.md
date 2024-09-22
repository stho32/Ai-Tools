# Convert a text into an audible book (mp3)

Split the text into chunks
```
python .\text_to_chunks.py "C:\Projekte\Ai-News\SomeText.txt" .\temp_split\
```

Convert them into an mp3
```
python .\chunks_to_mp3.py .\temp_split\
```
