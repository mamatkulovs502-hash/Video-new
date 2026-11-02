import calendar
import os
import re
import time

import feedparser
import requests

FEEDS = [
    "https://petapixel.com/feed/",
    "https://nofilmschool.com/rss.xml",
    "https://www.newsshooter.com/feed/",
]
HOURS = 26
MAX_ITEMS = 10

TOKEN = os.environ["TELEGRAM_TOKEN"]
CHAT_ID = os.environ["TELEGRAM_CHAT_ID"]


def recent_items():
    cutoff = time.time() - HOURS * 3600
    items = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries:
            t = e.get("published_parsed") or e.get("updated_parsed")
            if t and calendar.timegm(t) >= cutoff:
                summary = re.sub(r"<[^>]+>", "", e.get("summary", "")).strip()
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": summary[:300],
                })
    return items


def translate(text):
    if not text:
        return ""
    try:
        r = requests.get(
            "https://translate.googleapis.com/translate_a/single",
            params={"client": "gtx", "sl": "en", "tl": "uz", "dt": "t", "q": text},
            timeout=30,
        )
        r.raise_for_status()
        return "".join(part[0] for part in r.json()[0] if part[0])
    except Exception as exc:
        print("Tarjima xatosi:", exc)
        return text


def send(text):
    r = requests.post(
        f"https://api.telegram.org/bot{TOKEN}/sendMessage",
        data={"chat_id": CHAT_ID, "text": text, "disable_web_page_preview": True},
        timeout=30,
    )
    r.raise_for_status()


def main():
    items = recent_items()[:MAX_ITEMS]
    if not items:
        print("Yangi maqola yo'q")
        return
    for item in items:
        title = translate(item["title"])
        summary = translate(item["summary"])
        text = title
        if summary:
            text += "\n\n" + summary
        text += "\n\n" + item["link"]
        send(text)
        time.sleep(1)


main()
