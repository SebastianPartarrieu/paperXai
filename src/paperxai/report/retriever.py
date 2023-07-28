import numpy as np
from scipy import spatial
import pandas as pd

from paperxai.llms.base import BaseLLM
from paperxai.loading import load_config
from paperxai.prompt.base import Prompt
import paperxai.constants as constants


class ReportRetriever:
    def __init__(
        self,
        language_model: BaseLLM,
        prompter: Prompt,
        papers_embedding: np.ndarray,
        df_papers: pd.DataFrame,
        path_to_config_file: str = constants.ROOT_DIR + "/config.yml",
    ):
        self.language_model = language_model
        self.prompter = prompter
        self.papers_embedding = papers_embedding
        self.df_papers = df_papers
        self.config = load_config(path_to_config_file)


    def print_report(self) -> None:
        """
        Pretty print for the report 
        """
        report_string = ""
        for section_title, section_info in self.report.items():
            report_string += "Section: " + section_title + "\n"
            for i in range(len(section_info["questions"])):
                report_string += f"Question: {section_info['questions'][i]}" + "\n"
                report_string+= f"LLM response: {section_info['chat_responses'][i]}" + "\n"
            report_string += "\n"
        print(report_string)
        self.report_string = report_string

    def create_report(self) -> dict:
        """
        Create report from config file by retrieving top k papers for each query
        and constructing a summary.
        """
        report = {}
        sections = self.config["sections"]
        for section_number, section_info in sections.items():
            print("Getting responses for section: " + section_info["title"])
            chat_responses = [
                self.get_chat_response_to_question(section_info["questions"][i]) for i in range(len(section_info["questions"]))
            ]
            report[section_info["title"]] = {
                "questions": section_info["questions"],
                "chat_responses": chat_responses,
            }
        self.report = report
        return report


    def get_chat_response_to_question(self, question: str) -> str:
        """
        Embed question, retrieved top k papers and feed them as context
        to the language model to get a summary
        """
        embedded_question = self.language_model.get_embeddings(question)
        top_k_papers = self.retrieve_top_k_papers(question, top_k = 3)
        prompt = self.prompter.create_prompt_for_report(
            question, top_k_papers
        )
        chat_response = self.language_model.get_chat_response(
            prompt
        )
        return chat_response

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
