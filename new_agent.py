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
ANTHROPIC_KEY = os.environ.get("ANTHROPIC_API_KEY")


def recent_items():
    cutoff = time.time() - HOURS * 3600
    items = []
    for url in FEEDS:
        feed = feedparser.parse(url)
        for e in feed.entries:
            t = e.get("published_parsed") or e.get("updated_parsed")
            if t and calendar.timegm(t) >= cutoff:
                items.append({
                    "title": e.get("title", ""),
                    "link": e.get("link", ""),
                    "summary": re.sub(r"<[^>]+>", "", e.get("summary", ""))[:600],
                })
    return items


def to_uzbek(item):
    if not ANTHROPIC_KEY:
        return item["title"]
    prompt = (
        "Quyidagi videografiya yangiligini o'zbek tiliga (lotin) o'gir: "
        "bitta sarlavha qatori, keyin 1-2 gapli qisqa xulosa. Boshqa narsa yozma.\n\n"
        f"Sarlavha: {item['title']}\nMatn: {item['summary']}"
    )
    try:
        r = requests.post(
            "https://api.anthropic.com/v1/messages",
            headers={
                "x-api-key": ANTHROPIC_KEY,
                "anthropic-version": "2023-06-01",
                "content-type": "application/json",
            },
            json={
                "model": "claude-haiku-5-5",
                "max_tokens": 400,
                "messages": [{"role": "user", "content": prompt}],
            },
            timeout=60,
        )
        r.raise_for_status()
        return r.json()["content"][0]["text"].strip()
    except Exception as exc:
        print("Tarjima xatosi:", exc)
        return item["title"]


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
        send(f"{to_uzbek(item)}\n\n{item['link']}")
        time.sleep(1)


if name == "__main__":
    main()
