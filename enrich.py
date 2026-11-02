from pydantic import BaseModel, Field
from typing import Literal
import asyncio
from ollama import AsyncClient
from collections import defaultdict

client = AsyncClient()


SYSTEM_PROMPT = """
You are tasked with analyzing whether the content of an article is AI-related. 
By AI-related, we mean could it interest an AI engineer, someone working with generative IA or someone using generative IA.
You will furthermore assign the article a category, an importance, and write a summary about the article.
"""

USER_MESSAGE = """
Analyze and classify the article you've been given.
"""


class ArticleAnalysis(BaseModel):
    is_ai_related: bool = Field(description="True only if the article is mainly about AI technology")
    category: Literal["models", "tools", "evaluation", "carbon footprint", "research", "business", "regulation", "other"]
    importance: int = Field(
        ge=1, le=5,
        description="1 = minor update, 3 = notable for practitioners, 5 = major industry news",
    )
    summary: str = Field(description="Two sentences, factual, no hype")



async def analyse_article(article):
    title = article["title"]
    text = article["text"]
    response = await client.chat(
        model="llama3.2",
        messages=[
            {"role": "system", "content": SYSTEM_PROMPT},
            {"role": "user", "content": f"{USER_MESSAGE}\n\nTitle: {title}\n\nArticle:\n{text[:3000]}"},
        ],
        format=ArticleAnalysis.model_json_schema(),
        options={"temperature": 0},
    )
    analysis = ArticleAnalysis.model_validate_json(response.message.content)
    return {**article, ** analysis.model_dump()}


async def analyse_all(articles):
    tasks = [analyse_article(a) for a in articles]
    return await asyncio.gather(*tasks)


def organize_articles(articles):
    ai_articles = [a for a in articles if a["is_ai_related"] and a["importance"] >= 3]
    ai_articles.sort(key=lambda a: a["importance"], reverse=True)

    groups = defaultdict(list)
    for article in ai_articles:
       groups[article["category"]].append(article)
    return groups