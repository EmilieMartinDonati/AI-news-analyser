from pydantic import BaseModel, Field
from typing import Literal
import asyncio
import logging
from ollama import AsyncClient
from collections import defaultdict

log = logging.getLogger("enrich")

client = AsyncClient(timeout=120)
semaphore = asyncio.Semaphore(3)

SYSTEM_PROMPT = """
You are tasked with analyzing whether the content of an article is AI-related.
By AI-related, we mean holds some relevance for a software developer building AI-assisted applications or packages.
You will furthermore assign the article a category, an importance, and write a summary about the article.
"""

USER_MESSAGE = """
Analyze and classify the article you've been given.
"""


Topic = Literal["rag", "agents", "models and releases", "evals", "llm-as-a-judge",
                "prompting", "fine-tuning", "vector databases", "mcp", "langchain ecosystem",
                "data curation", "cost monitoring", "carbon footprint", "other"]

class ArticleAnalysis(BaseModel):
    summary: str = Field(description="Three sentences, factual, no hype")
    is_ai_related: bool = Field(description="True only if the article is mainly about AI technology")
    topics: list[Topic] = Field(description="1 to 3 topics, most relevant first. Use 'other' only if nothing fits.")
    content_type: Literal["explainer", "tutorial", "release", "research", "opinion", "news"] = Field(
        description="explainer: explains how something works, theory first. tutorial: step-by-step practical guide. ..."
    )
    builder_relevance: int = Field(ge=1, le=5, description="How useful for a developer building GenAI apps. 1 = not actionable, 5 = directly changes how I build")
    importance: int = Field(ge=1, le=5, description="1 = minor update, 3 = notable for practitioners, 5 = major industry news")
    takeaway: str = Field(description="One sentence: what a builder can learn or do with this")



async def analyse_article(article):
    async with semaphore:
        title = article["title"]
        text = article["text"]
        log.info("analysing: %s", title[:40])
        response = await client.chat(
            model="llama3.2",
            messages=[
                {"role": "system", "content": SYSTEM_PROMPT},
                {"role": "user", "content": f"{USER_MESSAGE}\n\nTitle: {title}\n\nArticle:\n{text[:3000]}"},
            ],
            format=ArticleAnalysis.model_json_schema(),
            options={"temperature": 0, "num_predict": 600},
        )
        log.info("llm %s: %d in / %d out tokens, %.1fs",
            article["title"][:40], response.prompt_eval_count,
            response.eval_count, response.total_duration / 1e9)
        analysis = ArticleAnalysis.model_validate_json(response.message.content)
        return {**article, **analysis.model_dump()}


async def analyse_all(articles):
    tasks = [analyse_article(a) for a in articles]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    return [r for r in results if not isinstance(r, Exception)]


def organize_articles(articles):
    ai_articles = [
        a for a in articles
        if a["is_ai_related"] and a["builder_relevance"] >= 3
    ]
    log.info(f"Found {len(ai_articles)} that are ai_related and have build relevance >= 3")
    ai_articles.sort(
        key=lambda a: (a["builder_relevance"], a["importance"]),
        reverse=True,
    )

    groups = defaultdict(list)
    for article in ai_articles:
        main_topic = article["topics"][0] if article["topics"] else "other"
        groups[main_topic].append(article)
    log.info("topics: %s", ", ".join(f"{t} ({len(a)})" for t, a in groups.items()))
    return groups