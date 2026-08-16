import json
import os
import re
import urllib.request

INPUT_JSON_FILE = "trip-data.json"
OUTPUT_JSON_FILE = "trip-data.json"  # Overwrites input file with updated local image paths
IMAGE_DIR = "images"

# Ensure output image directory exists
os.makedirs(IMAGE_DIR, exist_ok=True)


def sanitize_filename(text):
  """Converts highlight text into a clean filename slug."""
  clean = re.sub(r"[^\w\s-]", "", text.lower())
  return re.sub(r"[-\s]+", "_", clean)


# 1. Load data from local JSON file
if not os.path.exists(INPUT_JSON_FILE):
  print(f"❌ Error: {INPUT_JSON_FILE} not found in current directory.")
  exit(1)

with open(INPUT_JSON_FILE, "r", encoding="utf-8") as f:
  trip_data = json.load(f)

headers = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML,"
        " like Gecko) Chrome/120.0.0.0 Safari/537.36"
    )
}

# 2. Iterate and download images
for location in trip_data:
  for highlight in location.get("highlights", []):
    url = highlight.get("image")
    text = highlight.get("text")

    # Skip items without an image or items already pointing to local paths
    if not url or url.startswith("./images/"):
      continue

    filename = f"{sanitize_filename(text)}.jpg"
    filepath = os.path.join(IMAGE_DIR, filename)

    print(f"Downloading: {text} -> {filepath}")

    try:
      req = urllib.request.Request(url, headers=headers)
      with urllib.request.urlopen(req) as response, open(
          filepath, "wb"
      ) as out_file:
        out_file.write(response.read())

      # Update path in object
      highlight["image"] = f"./images/{filename}"

    except Exception as e:
      print(f"  ❌ Failed to download image for '{text}': {e}")

# 3. Save updated trip_data back to JSON
with open(OUTPUT_JSON_FILE, "w", encoding="utf-8") as f:
  json.dump(trip_data, f, indent=2, ensure_ascii=False)

print(f"\nFinished! Images saved to ./{IMAGE_DIR}/ and updated JSON saved to {OUTPUT_JSON_FILE}")