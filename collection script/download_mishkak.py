
from pathlib import Path
from io import BytesIO
import hashlib
import requests
from PIL import Image
from ddgs import DDGS

TARGET = 100
OUT = Path("omani_mishkak_images")
OUT.mkdir(exist_ok=True)

QUERIES = [
    '"Omani Mishkak" food',
    '"Mishkak Oman" grilled meat',
    'traditional Omani mishkak skewers',
    'Omani mishkak barbecue',
    'Omani marinated meat skewers',
    'Mishkak street food Oman',
    'Omani beef mishkak',
    'Omani lamb mishkak',
    'مشاكيك عمانية',
    'مشاكيك عمان',
]

session = requests.Session()
session.headers.update({
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 Chrome/131.0 Safari/537.36"
    )
})

seen = set()
saved = 0

# Keep existing valid images when rerunning
for path in OUT.iterdir():
    if not path.is_file():
        continue
    try:
        with Image.open(path) as im:
            im.verify()

        digest = hashlib.sha256(path.read_bytes()).hexdigest()
        if digest not in seen:
            seen.add(digest)
            saved += 1
    except Exception:
        continue

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
                    data = response.content

                    if len(data) > 15 * 1024 * 1024:
                        continue

                    with Image.open(BytesIO(data)) as im:
                        im.verify()

                    with Image.open(BytesIO(data)) as im:
                        if im.width < 200 or im.height < 200:
                            continue

                        extensions = {
                            "JPEG": ".jpg",
                            "PNG": ".png",
                            "WEBP": ".webp",
                        }
                        ext = extensions.get(im.format)

                    if ext is None:
                        continue

                    digest = hashlib.sha256(data).hexdigest()
                    if digest in seen:
                        continue

                    filename = OUT / f"mishkak_{saved + 1:04d}{ext}"
                    filename.write_bytes(data)

                    seen.add(digest)
                    saved += 1
                    print(f"Saved {saved}/{TARGET}")

                except Exception:
                    continue

    except Exception as exc:
        print(f"Search failed for '{query}': {exc}")

print("\nDownload finished.")
print(f"Unique valid images: {saved}")
print(f"Saved to: {OUT.resolve()}")

if saved < TARGET:
    print("Fewer than 100 images found. Try again later.")
