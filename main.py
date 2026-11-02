
import os
import asyncio
from dotenv import load_dotenv

from collect import collect
from enrich import analyse_all, organize_articles
from digest import write_digest


load_dotenv(override=True)

API_KEY = os.getenv("OPENAI_API_KEY")

if not API_KEY.startswith("sk-proj") and not len(API_KEY) > 10:
    print("There is a problem with your api key")
else:
    print("The api key looks ok")  
 
 
if __name__ == "__main__":
    articles = collect()
    results = asyncio.run(analyse_all(articles[:3]))
    results_by_cat = organize_articles(results)
    write_digest(results_by_cat)