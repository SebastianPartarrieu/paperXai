import pandas as pd

BASE_SYSTEM_PROMPT = "You are an expert researcher in the field of artificial intelligence. You can accurately summarize a complex scientific abstract into a single sentence and use it to answer larger scientific questions. You should cite the papers in your answer to the question. When citing a paper, use the name of the author given to you as well as the date. "

class Prompt:

    def __init__(self, system_prompt:str = BASE_SYSTEM_PROMPT) -> None:
        self.system_prompt = system_prompt

    def create_prompt_for_report(self, question: str, relevant_papers: pd.DataFrame) -> str:
        """
        Create a prompt tailored to the report.
        """
        prompt = self.system_prompt + "\n"
        prompt += "Question: " + question + "\n"
        prompt += "The top 3 papers that are relevant to this question are: \n"
        for _, row in relevant_papers.iterrows():
            prompt += row["String_representation"]
        prompt += "Answer: "
        return prompt
