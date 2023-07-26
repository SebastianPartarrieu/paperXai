# paperXai

Current ambition: Your arXiv daily digest - brought to you by your favorite LLM provider.

This is a **very early-stage project** which aims to sift through all the latest papers in AI posted on arXiv and filter according to your interests before giving you a short summary. The main pain point we're trying to solve is the sheer mass and noise of current information around AI. Even when we keep it to the latest papers, it's very hard to select the most interesting ones.

Future ambitions: aggregate across multiple news sources and create a fully automatic, personalized, newsletter that we can each tweak according to what we want to read. There are a few great newsletters out there and I'm not saying these will be out of business just yet; however, why can't I read something completely tailored to my interests that was intelligently put together and contains actionable information?

# Installation
- `conda env create -f environment.yml`
- `pip install -r requirements.txt`
- `pip install -e .`
- go to `src/paperxai`, create a `credentials.py` file and enter fill in `OPENAI_API_KEY = "your-key-here"`

# How to use this

# Development
Any contributions are welcome. Starting out as a solo project, I took the **very bad** habit of using only the master branch before using a cleaner feature branch based development process.

# Thanks
Thank you to arXiv for use of its open access interoperability.