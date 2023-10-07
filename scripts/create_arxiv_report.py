import pandas as pd
import numpy as np
import openai
import argparse

import paperxai.constants as constants
import paperxai.credentials as credentials
from paperxai.llms import NAME_TO_LLM
from paperxai.papers import Arxiv
from paperxai.report.retriever import ReportRetriever
from paperxai.prompt.base import Prompt
from paperxai.loading import load_config

openai.api_key = credentials.OPENAI_API_KEY

parser = argparse.ArgumentParser(description="Create a report based off the latest arXiv papers and your questions/sections defined in config.yml")
parser.add_argument(
    "--path_config",
    type=str,
    default=constants.ROOT_DIR + "/config.yml",
    help="path to config file",
)
args = parser.parse_args()


if __name__ == "__main__":
    config = load_config(args.path_config)
    language_model = NAME_TO_LLM[config["language_model"]["provider"]](
        **config["language_model"]["init_args"]
    )
    # get arxiv papers
    arxiv = Arxiv()
    arxiv.get_papers(categories=config["arxiv-categories"], max_results=int(config["max_papers"]))
    arxiv.write_papers()
    # load papers and compute embeddings
    df_papers = pd.read_csv(constants.ROOT_DIR + "/data/arxiv/current_papers.csv",
                            parse_dates=["Published Date"])
    df_papers["Embeddings"] = df_papers["String_representation"].apply(
    lambda x: language_model.get_embeddings(text=x)
)
    papers_embeddings = df_papers["Embeddings"].values
    papers_embeddings = np.vstack(papers_embeddings)
    # save embeddings
    np.save(constants.ROOT_DIR + "/data/arxiv/papers_embeddings.npy", papers_embeddings)
    # create report
    prompter = Prompt()
    report_retriever = ReportRetriever(
        language_model=language_model,
        prompter=prompter,
        papers_embedding=papers_embeddings,
        df_papers=df_papers,
        path_to_config_file=args.path_config,
    )
    report_retriever.create_report()
    report_retriever.print_report()
    report_retriever.write_report(format="html")
