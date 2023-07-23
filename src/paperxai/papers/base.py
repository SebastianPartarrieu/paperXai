import os
from abc import ABC, abstractmethod
import pandas as pd

import paperxai.constants as constants


class BasePapers(ABC):
    def __init__(
        self,
        source: str,
        base_papers_file_name: str = "base_papers.csv",
        current_papers_file_name: str = "current_papers.csv",
    ) -> None:
        self.source = source  # arxiv, pubmed, etc.
        self.data_folder = constants.ROOT_DIR + "/data/" + self.source
        # create data save folder based off source name
        if not os.path.exists(self.data_folder):
            os.makedirs(self.data_folder)
        self.base_papers_file_name = base_papers_file_name
        self.current_papers_file_name = current_papers_file_name
        self.path_base_papers = self.data_folder + "/" + self.base_papers_file_name
        self.path_current_papers = (
            self.data_folder + "/" + self.current_papers_file_name
        )
        # checks
        assert hasattr(self, "base_url"), "BasePapers must have a base_url attribute"
        assert hasattr(
            self, "query_params"
        ), "BasePapers must have a query_params attribute"

    @abstractmethod
    def get_papers(self, categories: list[str], max_results: int = 100) -> None:
        pass

    @abstractmethod
    def parse_paper_information_from_response(self, response: str) -> pd.DataFrame:
        pass

    @abstractmethod
    def write_papers(self) -> None:
        pass
