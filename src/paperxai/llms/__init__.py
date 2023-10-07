from paperxai.llms.base import BaseLLM
from paperxai.llms.openai import OpenAI

__all__ = ["OpenAI", "BaseLLM"]

NAME_TO_LLM = {"openai": OpenAI}
