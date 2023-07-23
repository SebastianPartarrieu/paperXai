from typing import List
import openai
import tiktoken
import numpy as np
from tenacity import retry, wait_random_exponential, stop_after_attempt

from paperxai.llms import BaseLLM


class OpenAI(BaseLLM):
    def __init__(
        self,
        chat_model: str = "gpt-3.5-turbo",
        embedding_model: str = "text-embedding-ada-002",
        temperature: int = 0.0,
        max_tokens: int = 1000,
    ) -> None:
        self.chat_model = chat_model
        self.embedding_model = embedding_model
        super().__init__(provider="openai")
        self.temperature = temperature
        self.max_tokens = max_tokens

    def set_tokenizer(self):
        self.tokenizer = tiktoken.get_encoding(self.chat_model)

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def get_chat_response(self, prompt: str) -> str:
        response = openai.ChatCompletion.create(
            model=self.chat_model,
            messages=[{"role": "user", "content": prompt}],
            temperature=self.temperature,
            max_tokens=self.max_tokens,
        )
        return response["choices"][0]["message"]["content"]

    @retry(wait=wait_random_exponential(min=1, max=10), stop=stop_after_attempt(3))
    def get_embedding(self, text: str) -> np.ndarray:
        embedding = openai.Embedding.create(
            model=self.embedding_model,
            input=[text],
        )
        return embedding["data"][0]["embedding"]

    def get_function_call_response(self) -> str:
        pass
