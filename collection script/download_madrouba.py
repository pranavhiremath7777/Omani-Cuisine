
import os
import hashlib
import requests
from io import BytesIO
from PIL import Image
from ddgs import DDGS

# Settings
TARGET_IMAGES = 100
OUTPUT_DIR = "omani_madrouba_images"

SEARCH_QUERIES = [
    "Omani Madrouba traditional food",
    "Madrouba Oman chicken rice porridge",
    "Omani madrouba dish",
    "Madrouba Arabic food",
    "traditional Omani Madrouba served plate",
    "Oman Madrouba chicken",
]

os.makedirs(OUTPUT_DIR, exist_ok=True)

seen_hashes = set()
downloaded = 0


def download_image(url):
    global downloaded

    try:
        headers = {
            "User-Agent": (
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                "AppleWebKit/537.36 Chrome/120.0 Safari/537.36"
            )
        }

        response = requests.get(
            url,
            headers=headers,
            timeout=15,
            stream=True
        )
        response.raise_for_status()

        content = response.content

        if not content:
            return False

        image_hash = hashlib.sha256(content).hexdigest()

        if image_hash in seen_hashes:
            return False

        image = Image.open(BytesIO(content))
        image.verify()

        # Reopen and convert to a standard image format
        image = Image.open(BytesIO(content)).convert("RGB")

        if image.width < 100 or image.height < 100:
            return False

        filename = os.path.join(
            OUTPUT_DIR,
            f"madrouba_{downloaded + 1:03d}.jpg"
        )

        image.save(filename, "JPEG", quality=95)

        seen_hashes.add(image_hash)
        downloaded += 1

        print(f"Downloaded {downloaded}/{TARGET_IMAGES}: {filename}")
        return True

    except Exception:
        return False


def main():
    global downloaded

    with DDGS() as ddgs:
        for query in SEARCH_QUERIES:
            if downloaded >= TARGET_IMAGES:
                break

            print(f"\nSearching: {query}")

            try:
                results = ddgs.images(
                    query,
                    max_results=150
                )

                for result in results:
                    if downloaded >= TARGET_IMAGES:
                        break

                    image_url = result.get("image")

                    if image_url:
                        download_image(image_url)

            except Exception as error:
                print(f"Search error: {error}")

    print("\nDownload finished.")
    print(f"Total unique images downloaded: {downloaded}")
    print(f"Saved in: {os.path.abspath(OUTPUT_DIR)}")

    if downloaded < TARGET_IMAGES:
        print(
            "Could not reach 100 images. "
            "Try running the script again or adding more search queries."
        )


if __name__ == "__main__":
    main()
