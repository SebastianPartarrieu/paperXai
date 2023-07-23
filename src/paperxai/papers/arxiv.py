import os
import requests
import pandas as pd
from bs4 import BeautifulSoup

import paperxai.constants as constants
from paperxai.papers import BasePapers


class Arxiv(BasePapers):
    def __init__(
        self,
        base_url: str = "http://export.arxiv.org/api/query",
        query_params: dict = constants.ARXIV_BASE_QUERY_PARAMS,
        base_papers_file_name: str = "base_papers.csv",
        current_papers_file_name: str = "current_papers.csv",
    ) -> None:
        self.base_url = base_url
        self.query_params = query_params
        super().__init__(
            source="arxiv",
            base_papers_file_name=base_papers_file_name,
            current_papers_file_name=current_papers_file_name,
        )
        self.df_papers = None

    def get_papers(self, categories: list[str], max_results: int = 100) -> None:
        """
        Get the latest papers from the arXiv API using the specified categories.
        """
        # format categories and update query params
        category_query = "".join(
            ["cat:" + category + " OR " for category in categories]
        )[:-4]
        self.query_params["search_query"] = category_query
        self.query_params["max_results"] = max_results

        # get API response
        response = requests.get(self.base_url, params=self.query_params)
        # parse and store response
        self.df_papers = self.parse_paper_information_from_response(response)

    def parse_paper_information_from_response(self, response: str) -> pd.DataFrame:
        """
        Parse the response from the arXiv API.
        The folliwing links may be useful to understand the various fields:
        https://info.arxiv.org/help/prep.html#subj
        https://info.arxiv.org/help/api/user-manual.html#_calling_the_api
        """
        if response.status_code != 200:
            print("Failed to fetch data from arXiv API.")
            return
        soup = BeautifulSoup(response.content, "xml")
        entries = soup.find_all("entry")
        papers_data = []
        for entry in entries:
            title = entry.title.text
            url = entry.link["href"]
            abstract = entry.summary.text.strip()
            authors = ", ".join(
                [author.find("name").text for author in entry.find_all("author")]
            )
            published_date = entry.published.text
            category = entry.category["term"]  # primary category
            paper_id = entry.id.text.split("/")[-1]  # arXiv identifier
            paper_data = {
                "Title": title,
                "URL": url,
                "Abstract": abstract,
                "Authors": authors,
                "Published Date": published_date,
                "Category": category,
                "Paper ID": paper_id,
            }
            papers_data.append(paper_data)
        return pd.DataFrame(papers_data)

    def write_papers(self) -> None:
        """
        Write the papers into a pandas DataFrame.
        Two files are written and stored:
        - base_papers.csv: contains the base dataframe of all previous papers. This dataframe
        is filtered to not contain papers older than 3 months old and is continuously updated.
        - current_papers.csv: contains the current dataframe of papers. These papers
        consist of the papers that were obtained from the last API call and were not previously
        stored in the base_papers.csv file.
        """
        if self.df_papers is None:
            print("No papers to write, make sure to run the `get_papers` method first.")
            return
        # check old papers exist and if not, write new papers to file
        if not os.path.exists(self.path_base_papers):
            self.df_papers.to_csv(self.path_base_papers, index=False)
            self.df_papers.to_csv(self.path_current_papers, index=False)
            return
        # load old papers
        df_old_papers = pd.read_csv(self.path_base_papers)
        # get new papers that are not in old papers
        df_new_papers = self.df_papers[
            ~self.df_papers["paper ID"].isin(df_old_papers["paper ID"])
        ]
        # write new papers
        df_new_papers.to_csv(
            self.path_current_papers,
            index=False,
        )
        # combine old and new papers
        df_all_papers = pd.concat([df_old_papers, self.df_papers])
        df_all_papers = df_all_papers.drop_duplicates(subset=["Paper ID"])
        # remove those more than 3 months old
        df_all_papers["Published Date"] = pd.to_datetime(
            df_all_papers["Published Date"]
        )
        df_all_papers = df_all_papers[
            df_all_papers["Published Date"]
            > pd.to_datetime("today") - pd.DateOffset(months=3)
        ]
        # write all papers
        df_all_papers.to_csv(self.path_base_papers, index=False)
        print("Data saved successfully.")
