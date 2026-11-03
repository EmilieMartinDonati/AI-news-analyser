
import feedparser
import json
import logging
from trafilatura import fetch_url, extract

log = logging.getLogger("collect")

FEEDS = [
        "https://magazine.sebastianraschka.com/feed",
        "https://simonwillison.net/atom/everything/",
        "https://medium.com/feed/@cameronrwolfe",
        "https://medium.com/feed/@pavanbelagatti",
        "https://medium.com/feed/towards-artificial-intelligence",
        "https://medium.com/feed/@adilshamim8",
        "https://medium.com/feed/generative-ai",
        "https://medium.com/feed/ai-engineering-compass",
        "https://medium.com/feed/@Pop123",
        # "https://huggingface.co/blog/feed.xml",
        # "https://rss.arxiv.org/rss/cs.AI",
        # "https://www.technologyreview.com/topic/artificial-intelligence/feed",
   ]


def fetch_article(url):
    html = fetch_url(url)
    if html is None:
        return None
    result = extract(html, output_format="json", with_metadata=True)
    if result is None:
        log.warning("download failed: %s", url)
        return None
    data = json.loads(result) # converts string to dict
    return {
        "title": data.get("title"),
        "text": data.get("text") or data.get("raw_text") or "",
        "source": url,
        "date": data.get("date"),
    }

def text_from_entry(entry):
    if "content" in entry:                 # full HTML of the article
        html = entry.content[0].value
    else:
        html = entry.get("summary", "")
    return extract(html) or ""

def collect():
    articles = []
    for feed in FEEDS:
        parsed = feedparser.parse(feed)
        log.info("%s: %d entries", feed, len(parsed.entries))
        for entry in parsed.entries[:3]:
            text = text_from_entry(entry)
            if len(text) > 500:            # enough content in the feed
                articles.append({
                    "title": entry.title,
                    "text": text,
                    "source": entry.link,
                    "date": entry.get("published"),
                })
            else:
                fetched = fetch_article(entry.link)
                if fetched:
                    articles.append(fetched)
                elif text:                                  # download refused: keep the preview
                    articles.append({"title": entry.title, "text": text,
                                    "source": entry.link, "date": entry.get("published"),
                                    "is_preview": True})
    return articles