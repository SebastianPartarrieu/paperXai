import numpy as np
from scipy import spatial
import pandas as pd

from paperxai.llms.base import BaseLLM
from paperxai.loading import load_config
import paperxai.constants as constants


class ReportRetriever:
    def __init__(
        self,
        language_model: BaseLLM,
        papers_embedding: np.ndarray,
        df_papers: pd.DataFrame,
        path_to_config_file: str = constants.ROOT_DIR + "config.yml",
    ):
        self.language_model = language_model
        self.papers_embedding = papers_embedding
        self.df_papers = df_papers
        self.config = load_config(path_to_config_file)

    def create_report(self) -> None:
        """
        Create report from config file by retrieving top k papers for each query
        and constructing a summary.
        """
        pass

    def retrieve_top_k_papers(self, query: str, top_k: int = 10) -> list[int]:
        """
        Retrieve top k papers given query.
        """
        query_embedding = self.language_model.get_embeddings(query)
        query_embedding = np.array(query_embedding)
        # calculate cosine similarity between query and all papers
        cosine_similarities = np.array(
            [
                self.similarity_function(query_embedding, paper_embedding)
                for paper_embedding in self.papers_embedding
            ]
        )
        # get top k paper indices
        top_k_papers_indices = np.argsort(cosine_similarities)[::-1][:top_k]
        # take top k papers from dataframe
        top_k_papers = self.df_papers.iloc[top_k_papers_indices]
        return top_k_papers

    def similarity_function(self, query: str, paper_embedding: str) -> float:
        """
        Calculate similarity between query and embedding
        """
        return 1 - spatial.distance.cosine(query, paper_embedding)
