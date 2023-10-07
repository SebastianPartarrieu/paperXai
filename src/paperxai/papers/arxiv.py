import os
import requests
from datetime import datetime, timedelta, timezone
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

    def get_papers(self, categories: list[str], max_results: int = 1000) -> None:
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
        paper_data = self.format_dataframe(pd.DataFrame(papers_data))
        return paper_data

    def format_dataframe(self, papers_data: pd.DataFrame) -> pd.DataFrame:
        """
        Format the papers dataframe, including dates and creating a string representation
        for later embedding.
        """
        papers_data["String_representation"] = papers_data.apply(
            lambda x: self.create_string_to_embed(x), axis=1
        )
        papers_data["Published Date"] = pd.to_datetime(
            papers_data["Published Date"]
        ).dt.tz_convert(timezone.utc)
        return papers_data

    def create_string_to_embed(self, row: pd.Series) -> str:
        """
        Create a single string representation of an article to embed.
        """
        article_string_representation = (
            "Title: "
            + row["Title"]
            + "\n"
            + "Abstract: "
            + row["Abstract"]
            + "\n"
            + "First Author: "
            + row["Authors"].split(",")[0]
            + "\n"
            + "Published Date: "
            + row["Published Date"].split("T")[0]
            + "\n"
        )
        return article_string_representation

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
        df_old_papers = pd.read_csv(self.path_base_papers,
                                    parse_dates=["Published Date"])
        # check whether you've updated the base papers less than one day ago
        if not self.check_whether_should_write_papers(df_old_papers):
            raise Exception("You've already updated the base papers less than one day ago. Not updating.")
        # get new papers that are not in old papers
        df_new_papers = self.df_papers[
            ~self.df_papers["Paper ID"].isin(df_old_papers["Paper ID"])
        ]
        # write new papers
        df_new_papers.to_csv(
            self.path_current_papers,
            index=False,
        )
        # update old papers and remove those more than 3 months old
        df_all_papers = pd.concat([df_old_papers, self.df_papers])
        df_all_papers = df_all_papers.drop_duplicates(subset=["Paper ID"])
        current_date = datetime.now(timezone.utc)
        cutoff_date = current_date - timedelta(days=3 * 30)
        df_all_papers = df_all_papers[df_all_papers["Published Date"] >= cutoff_date]
        # write all papers
        df_all_papers.to_csv(self.path_base_papers, index=False)
        print("Data saved successfully.")


    def check_whether_should_write_papers(self, df_old_papers:pd.DataFrame) -> bool:
        """
        Checks whether the last time the papers were written was more than one day ago.
        """
        last_write_date = df_old_papers["Published Date"].max()
        current_date = datetime.now(timezone.utc)
        return (current_date - last_write_date) > timedelta(days=1)
