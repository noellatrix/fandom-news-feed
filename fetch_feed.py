import json
import urllib.request
from xml.etree import ElementTree
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime

FEED_GROUPS = [
    {
        "label": "The Daily Prophet",
        "feeds": [
            "https://mugglenet.com/feed",
        ],
    },
    {
        "label": "Disney News",
        "feeds": [
            "https://www.disneyfoodblog.com/feed/",
            "https://wdwnt.com/feed/",
        ],
    },
]

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
    "Accept-Language": "en-US,en;q=0.5",
    "Accept-Encoding": "identity",
    "Connection": "keep-alive",
}

def fetch_items(url):
    try:
        req = urllib.request.Request(url, headers=HEADERS)
        with urllib.request.urlopen(req, timeout=10) as res:
            print(f"  HTTP status: {res.status}")
            raw = res.read()
            xml = ElementTree.fromstring(raw)
    except Exception as e:
        print(f"  Failed to fetch {url}: {e}")
        return []

    items = []
    for item in xml.iter("item"):
        title = item.findtext("title", "").strip()
        link  = item.findtext("link", "").strip()
        date  = item.findtext("pubDate", "").strip()

        if not link:
            el = item.find("link")
            if el is not None and el.tail:
                link = el.tail.strip()

        if not link:
            guid = item.findtext("guid", "").strip()
            if guid.startswith("http"):
                link = guid

        if not title or not link:
            continue

        try:
            parsed_date = parsedate_to_datetime(date)
        except Exception:
            parsed_date = datetime.now(timezone.utc)

        items.append({
            "title":    title,
            "link":     link,
            "date":     parsed_date.strftime("%-d %b"),
            "sort_key": parsed_date.timestamp(),
        })

    print(f"  Found {len(items)} items")
    return items


output = []
for group in FEED_GROUPS:
    print(f"Fetching group: {group['label']}")
    all_items = []
    for url in group["feeds"]:
        print(f"  {url}")
        all_items.extend(fetch_items(url))

    all_items.sort(key=lambda x: x["sort_key"], reverse=True)
    for item in all_items:
        del item["sort_key"]

    output.append({
        "label": group["label"],
        "items": all_items[:5],
    })

with open("feed.json", "w") as f:
    json.dump(output, f, indent=2)

print("Done — feed.json written.")
