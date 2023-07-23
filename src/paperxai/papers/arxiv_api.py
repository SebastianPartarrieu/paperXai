# script to obtain papers from the arXiv API
import requests
import pandas as pd
from bs4 import BeautifulSoup

import paperxai.constants as constants

url = "http://export.arxiv.org/api/query"


def get_latest_ai_articles():
    base_url = "http://export.arxiv.org/api/query"
    params = {
        "search_query": "cat:cs.AI",
        "sortBy": "lastUpdatedDate",
        "sortOrder": "descending",
        "max_results": 100,
    }

    response = requests.get(base_url, params=params)

    if response.status_code != 200:
        print("Failed to fetch data from arXiv API.")
        return

    soup = BeautifulSoup(response.content, "xml")
    entries = soup.find_all("entry")

    articles_data = []

    for entry in entries:
        title = entry.title.text
        url = entry.link["href"]
        abstract = entry.summary.text.strip()
        authors = ", ".join(
            [author.find("name").text for author in entry.find_all("author")]
        )

        article_data = {
            "Title": title,
            "URL": url,
            "Abstract": abstract,
            "Authors": authors,
        }

        articles_data.append(article_data)

    df = pd.DataFrame(articles_data)
    df.to_csv(constants.ROOT_DIR + "/data/arxiv_articles.csv", index=False)
    print("Data saved to arxiv_articles.csv successfully.")


if __name__ == "__main__":
    get_latest_ai_articles()
