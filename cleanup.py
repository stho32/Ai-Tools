import os

# Get the current directory
current_directory = os.getcwd()

# Iterate through all files in the current directory
for filename in os.listdir(current_directory):
    # Check if the file is a .txt or .mp3 file
    if filename.endswith(".txt") or filename.endswith(".mp3"):
        file_path = os.path.join(current_directory, filename)
        try:
            # Delete the file
            os.remove(file_path)
            print(f"Deleted: {filename}")
        except Exception as e:
            print(f"Error deleting {filename}: {e}")

print("Cleanup complete.")
