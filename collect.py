
import feedparser
import json

from trafilatura import fetch_url, extract

FEEDS = [
       "https://huggingface.co/blog/feed.xml",
       "https://rss.arxiv.org/rss/cs.AI",
       "https://www.technologyreview.com/topic/artificial-intelligence/feed",
   ]

def collect():
    articles = []
    for feed in FEEDS:
        parsed = feedparser.parse(feed)
        for entry in parsed.entries[:3]:
            if entry.link:
                fetched = fetch_article(entry.link)
                if fetched:
                    articles.append(fetched)

    return articles


def fetch_article(url):
    html = fetch_url(url)
    if html is None:
        return None
    result = extract(html, output_format="json", with_metadata=True)
    if result is None:
        return None
    data = json.loads(result) # converts string to dict
    return {
        "title": data.get("title"),
        "text": data.get("text") or data.get("raw_text") or "",
        "source": url,
        "date": data.get("date"),
    }
