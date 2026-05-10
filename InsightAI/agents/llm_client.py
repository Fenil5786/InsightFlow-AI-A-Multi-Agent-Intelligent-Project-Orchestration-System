import os
import asyncio
from typing import Dict, List

from dotenv import load_dotenv
from openai import AsyncOpenAI
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import (
    OpenAIChatCompletion,
    OpenAIChatPromptExecutionSettings,
)
from semantic_kernel.contents import ChatHistory

load_dotenv()

GROQ_API_KEY = os.getenv("GROQ_API_KEY")
MODEL = os.getenv("GROQ_MODEL", "openai/gpt-oss-120b")
BASE_URL = "https://api.groq.com/openai/v1"


class SemanticKernelClient:
    def __init__(self, model: str, api_key: str, base_url: str) -> None:
        self.kernel = Kernel()
        async_client = AsyncOpenAI(api_key=api_key, base_url=base_url)
        self.chat_service = OpenAIChatCompletion(
            ai_model_id=model,
            api_key=api_key,
            async_client=async_client,
            service_id="default",
        )
        self.kernel.add_service(self.chat_service)

    async def _complete_async(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> str:
        history = ChatHistory()
        for msg in messages:
            role = (msg.get("role") or "user").lower()
            content = msg.get("content") or ""
            if role == "system":
                history.add_system_message(content)
            elif role == "assistant":
                history.add_assistant_message(content)
            else:
                history.add_user_message(content)

        settings = OpenAIChatPromptExecutionSettings(
            temperature=temperature,
            max_tokens=1200,
        )
        result = await self.chat_service.get_chat_message_contents(
            chat_history=history,
            settings=settings,
            kernel=self.kernel,
        )

        return result[0].content if result else ""

    def complete(self, messages: List[Dict[str, str]], temperature: float = 0.0) -> str:

        try:
            return asyncio.run(self._complete_async(messages, temperature))
        except RuntimeError:
            loop = asyncio.new_event_loop()
            try:
                return loop.run_until_complete(self._complete_async(messages, temperature))
            finally:
                loop.close()


client = SemanticKernelClient(model=MODEL, api_key=GROQ_API_KEY, base_url=BASE_URL)
