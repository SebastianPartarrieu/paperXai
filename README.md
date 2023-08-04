# paperXai [![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT) ![Python](https://img.shields.io/badge/python-3.9-blue.svg) [![PRs Welcome](https://img.shields.io/badge/PRs-welcome-brightgreen.svg?style=flat-square)](http://makeapullrequest.com)

Current ambition: Your arXiv daily digest - brought to you by your favorite LLM provider.

This is a **very early-stage project** which aims to sift through all the latest papers in AI posted on arXiv and filter according to your interests before giving you a short summary. The main pain point we're trying to solve is the sheer mass and noise of current information around AI.

Future ambitions: aggregate across multiple news sources/paper repositories and create a fully automatic, personalized, newsletter that we can each tweak according to what we want to read. There are a few great newsletters out there and I'm not saying these will be out of business just yet; however, why can't I read something completely tailored to my interests?

## Installation

If you already have miniconda installed (if not go install it):

- `conda env create -f environment.yml`
- `pip install -r requirements.txt`
- `pip install -e .`
- go to `src/paperxai`, create a `credentials.py` file and enter fill in `OPENAI_API_KEY = "your-key-here"`

Once you've finished the installation procedure, a good place to start may the `notebooks/example_workflow.ipynb` notebook which gives a good overview of the different parts of the package.

## Usage

Most important details of the report are defined in the `config.yml` file (sections, questions, llm provider ...). You should start by having a look at this file if you want to understand what is easily customizable for your report.

### Option #1 -> run a script or notebook

`conda activate llms`

`python scripts/create_arxiv_report --path_config config.yml`

`open display/reports/{Y-m-d}-report.html`: this should open the report in your browser to make it easier to read

You can follow the details of the script workflow in the notebook for an overview of the details of how we create the report.

### Option #2 (Incoming) -> use the streamlit webapp

`cd display`

`streamlit run webapp.py`

### Option #3 (Incoming) -> through the newsletter service

- Fill in questionnaire to define sections and questions
- Receive updates at the frequency of your choice with the report in the email

## Testing

## Development

Any contributions are welcome. Starting out as a solo project, I took the **very bad** habit of using only the master branch before using a cleaner feature branch based development process. There are also some arbitrary choices that have been made (such as using some minimalist modules instead of using libraries like langchain).

(checklist) before pushing changes or opening a PR:

- `pip list --format=freeze > requirements.txt`
- remove `paperxai` from the requirements and add `pip install -e .`

### TODO

(Not necessarily in order of priority)

- [x] Write script to run report creation from CLI
- [ ] More formats for the report (e.g markdown, pdf)
- [ ] Quick streamlit webapp where you enter api key, launch report creation and it loads the report directly
- [ ] Work further on report style
- [ ] Handle pubmed API and adapt report creation code
- [ ] Support email integration to receive it automatically
- [ ] Handle document batching and retrieval from the whole paper for those selected based off abstract

## Disclaimer

This does not substitute discovering papers/information through the multitude of other ways. It's useful if you have a few predefined topics and want to sift through the volume of incoming information. It's also a toy project.

## Thanks

Thank you to arXiv for use of its open access interoperability.
