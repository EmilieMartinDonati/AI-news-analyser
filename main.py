
import os
import asyncio
from dotenv import load_dotenv
from observability import setup_logging, stage, log

from collect import collect
from enrich import analyse_all, organize_articles
from digest import write_digest

TEST_LIMIT = 5

load_dotenv(override=True)

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY.startswith("sk-proj") and not len(API_KEY) > 10:
    print("There is a problem with your api key")
else:
    print("The api key looks ok")  
 
 
if __name__ == "__main__":
    setup_logging()
    with stage("collect"):
        articles = collect()
    log.info("collected %d articles", len(articles))
    with stage("analyse"):
        results = asyncio.run(analyse_all(articles[:TEST_LIMIT]))
    log.info("analysed %d results", len(results))
    with stage("organize"):
        results_by_cat = organize_articles(results)
    with stage("digest"):
        write_digest(results_by_cat)