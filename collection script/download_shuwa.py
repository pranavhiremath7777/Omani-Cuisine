
from pathlib import Path
from io import BytesIO
import hashlib
import requests
from PIL import Image
from ddgs import DDGS

TARGET = 100
OUT = Path("omani_shuwa_images")
OUT.mkdir(exist_ok=True)

QUERIES = [
    '"Omani Shuwa" food',
    '"Shuwa" Oman traditional meat',
    'Omani Shuwa lamb',
    'Omani Shuwa Eid',
    'Omani Shuwa traditional cooking',
    'Oman shuwa roasted meat',
]

seen = set()
saved = 0

# Keep existing valid images and avoid downloading them again
for path in OUT.iterdir():
    try:
        with Image.open(path) as im:
            im.verify()
        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        seen.add(digest)
        saved += 1
    except Exception:
        pass

session = requests.Session()
session.headers.update({
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
                  "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
})

for query in QUERIES:
    if saved >= TARGET:
        break

    print(f"\nSearching: {query}")

    try:
        with DDGS() as search:
            results = search.images(query, max_results=100)

            for result in results:
                if saved >= TARGET:
                    break

                url = result.get("image")
                if not url:
                    continue

                try:
                    response = session.get(url, timeout=15)
                    response.raise_for_status()

                    # Ignore very large downloads
                    if len(response.content) > 15 * 1024 * 1024:
                        continue

                    with Image.open(BytesIO(response.content)) as im:
                        im.verify()

                    with Image.open(BytesIO(response.content)) as im:
                        if im.width < 200 or im.height < 200:
                            continue
                        image_format = im.format
                        extension = Image.registered_extensions()
                        ext = next(
                            (e for e, fmt in extension.items()
                             if fmt == image_format and e in
                             (".jpg", ".jpeg", ".png", ".webp")),
                            ".jpg"
                        )

                    digest = hashlib.sha256(response.content).hexdigest()
                    if digest in seen:
                        continue

                    saved += 1
                    filename = OUT / f"shuwa_{saved:04d}{ext}"
                    filename.write_bytes(response.content)
                    seen.add(digest)

                    print(f"Saved {saved}/{TARGET}")

                except Exception:
                    continue

    except Exception as exc:
        print(f"Search failed: {exc}")

print(f"\nFinished. Total unique images: {saved}")
print(f"Folder: {OUT.resolve()}")

if saved < TARGET:
    print("Fewer than 100 images found. Run again later or add queries.")
