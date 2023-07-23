from abc import ABC, abstractmethod
from typing import List
import numpy as np


class BaseLLM(ABC):
    def __init__(self, provider: str):
        self.provider = provider
        self.set_tokenizer()
        # ensure that the tokenizer has an encode method
        assert hasattr(self.tokenizer, "encode"), "Tokenizer must have an encode method"

    @abstractmethod
    def set_tokenizer(self) -> None:
        pass

    @abstractmethod
    def get_embeddings(self, text: List[str]) -> np.ndarray:
        pass

    @abstractmethod
    def get_chat_response(self, prompt: str) -> str:
        pass

    def get_token_length_of_string(self, text: str) -> int:
        return len(self.tokenizer.encode(text))
