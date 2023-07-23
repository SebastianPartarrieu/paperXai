# automatically get root path of once removed parent folder

from pathlib import Path

ROOT_DIR = str(Path(__file__).parents[2])

# papers specific constants
ARXIV_BASE_QUERY_PARAMS = {
    "search_query": "cat:cs.AI",
    "sortBy": "submittedDate",
    "sortOrder": "descending",
    "max_results": 1000,
}
