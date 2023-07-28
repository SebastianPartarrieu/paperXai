# script to obtain papers from the arXiv API
import argparse

from paperxai.papers import Arxiv
import paperxai.constants as constants
from paperxai.loading import load_config

# parse arguments
parser = argparse.ArgumentParser(description="Get latest AI papers from arXiv API")
parser.add_argument(
    "--path_config",
    type=str,
    default=constants.ROOT_DIR + "/config.yml",
    help="path to config file",
)
parser.add_argument(
    "--max_results",
    type=int,
    default=1000,
    help="maximum number of results to return from arXiv API",
)
args = parser.parse_args()


if __name__ == "__main__":
    # load config yml file
    config = load_config(args.path_config)
    arxiv = Arxiv()
    arxiv.get_papers(categories=config["arxiv-categories"], max_results=args.max_results)
    arxiv.write_papers()