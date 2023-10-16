from typing import Optional, Union
from datetime import datetime, timezone
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
        path_to_config_file: Optional[str] = constants.ROOT_DIR + "/config.yml",
        config: dict[str, Union[str, dict]] = None,
    ):
        self.language_model = language_model
        self.prompter = prompter
        self.papers_embedding = papers_embedding
        self.df_papers = df_papers
        self.report = {}
        self.report_papers = pd.DataFrame()
        self.config = load_config(path_to_config_file)
        if config:
            self.config = config

    def write_report(self, format: str = "html") -> None:
        """
        Write the report to a file in the chosen format
        """
        if format == "html":
            self.write_html_report()
        elif format == "md":
            self.write_md_report()
        else:
            raise ValueError("Format not supported")
        
    def write_html_report(self) -> None:
        """
        Write the report to a html file using a template defined in `display/template.html`
        """
        if self.report == {}:
            raise ValueError("Report is empty. Please run `create_report` first")
        #get dates
        current_date = datetime.now(timezone.utc).strftime("%Y-%m-%d")
        oldest_date_in_report_papers = self.report_papers["Published Date"].min().strftime("%Y-%m-%d")
        report_html_string = self.format_report()
        with open(constants.ROOT_DIR + "/display/template.html", "r") as f:
            template_html_string = f.read()
        template_html_string = template_html_string.replace("{report_string}", report_html_string)
        template_html_string = template_html_string.replace("{oldest_paper_date_string}", oldest_date_in_report_papers)
        with open(constants.ROOT_DIR + "/display/reports/"+current_date+"-report.html", "w") as f:
            f.write(template_html_string)
        print(f"HTML is saved to /display/reports/{current_date}-report.html, open it in your browser to view the report")

    def write_md_report(self) -> None:
        """
        Write the report to a markdown file
        """
        pass

    def print_report(self) -> None:
        """
        Pretty print for the report 
        """
        report_string = ""
        for section_title, section_info in self.report.items():
            report_string += "Section: " + section_title + "\n\n"
            if isinstance(section_info["questions"], list):
                for i in range(len(section_info["questions"])):
                    report_string += f"Question: {section_info['questions'][i]}" + "\n"
                    report_string+= f"LLM response: {section_info['chat_responses'][i]}" + "\n"
                report_string += "\n"
        print(report_string)
        

    def format_report(self) -> None:
        report_html_string  = ""
        for section_title, section_info in self.report.items():
            report_html_string += "<h2> Section: " + section_title + "</h2>"
            if isinstance(section_info["questions"], list):
                for i in range(len(section_info["questions"])):
                    report_html_string += "<h3> Question: " + section_info['questions'][i] + "</h3>"
                    report_html_string += "<p> LLM response: " + section_info['chat_responses'][i] + "</p>"
                    # add papers
                    report_html_string += "<h4> Papers </h4>"
                    report_html_string += self.format_paper_df_to_html_citation(section_info['papers'][i])
        return report_html_string


    def format_paper_df_to_html_citation(self, df_papers:pd.DataFrame) -> pd.DataFrame:
        """
        Format the dataframe of papers to html citations
        """
        citation_list = []
        for _, row in df_papers.iterrows():
            citation_list.append(
                f"<li> {row['Title']}. {row['Authors'].split(',')[0].split(' ')[-1]} et al. {row['Published Date'].strftime('%Y')}</li>"
            )
        return "<ul>" + "".join(citation_list) + "</ul>"

    def create_report(self) -> dict:
        """
        Create report from config file by retrieving top k papers for each query
        and constructing a summary.
        """
        report = {}
        sections = self.config["sections"]
        for section_number, section_info in sections.items():
            print("Getting responses for section: " + section_info["title"])
            responses = [
                self.get_chat_response_and_papers_to_question(section_info["questions"][i]) for i in range(len(section_info["questions"]))
            ]
            chat_responses = [response[0] for response in responses]
            top_k_papers = [response[1] for response in responses]
            report[section_info["title"]] = {
                "questions": section_info["questions"],
                "chat_responses": chat_responses,
                "papers": top_k_papers
            }
        self.report = report
        return report


    def get_chat_response_and_papers_to_question(self, question: str) -> tuple[str, pd.DataFrame]:
        """
        Embed question, retrieved top k papers and feed them as context
        to the language model to get a summary
        """
        print("Answering question: " + question)
        top_k_papers = self.retrieve_top_k_papers(question, top_k = 3)
        self.report_papers = pd.concat([self.report_papers, top_k_papers])
        prompt = self.prompter.create_prompt_for_report(
            question, top_k_papers
        )
        chat_response = self.language_model.get_chat_response(
            prompt
        )
        return chat_response, top_k_papers

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
