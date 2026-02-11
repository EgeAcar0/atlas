import urllib.request
import zipfile
import os

url = "https://alphacephei.com/vosk/models/vosk-model-spk-0.4.zip"
dest = "vosk-model-spk.zip"
extract_to = "."

print(f"Downloading {url}...")
urllib.request.urlretrieve(url, dest)

print(f"Extracting {dest}...")
with zipfile.ZipFile(dest, 'r') as zip_ref:
    zip_ref.extractall(extract_to)

print("Cleaning up...")
os.remove(dest)
print("Done! Speaker model ready.")
