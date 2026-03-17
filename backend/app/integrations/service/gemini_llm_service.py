import logging
import os
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.messages import HumanMessage, SystemMessage, AIMessage

env_path = Path(__file__).parent.parent.parent.parent / ".env"
load_dotenv(dotenv_path=env_path)

logger = logging.getLogger(__name__)


class GeminiService:
    """Service for calling Google Gemini LLM."""

    def __init__(self, temperature: float = 0.2):
        """
        Initialize Gemini Service.

        Args:
            temperature: Model creativity level (0.0-1.0). Default 0.2 for factual responses.
        """
        try:
            self.gemini_api_key = os.getenv("GEMINI_API_KEY", "")

            if not self.gemini_api_key:
                raise ValueError("GEMINI_API_KEY not set in environment")

            logger.info("Initializing ChatGoogleGenerativeAI")
            self.llm = ChatGoogleGenerativeAI(
                model="gemini-2.5-flash-lite",
                temperature=temperature,
                google_api_key=self.gemini_api_key,
                convert_system_message_to_human=True,
            )
            logger.info(f"LLM initialized (temperature={temperature})")

        except Exception as e:
            logger.error(f"Failed to initialize GeminiService: {e}", exc_info=True)
            raise

    def generate(self, prompt: str, system_prompt: Optional[str] = None) -> str:
        """
        Generate text response from a prompt.

        Args:
            prompt: User prompt/question
            system_prompt: Optional system prompt to define bot behavior

        Returns:
            Generated response from LLM

        Raises:
            Exception: If API key is invalid or network error occurs
        """
        try:
            logger.info(f"Calling Gemini LLM")

            messages = []

            if system_prompt:
                messages.append(SystemMessage(content=system_prompt))

            messages.append(HumanMessage(content=prompt))

            response = self.llm.invoke(messages)
            result = response.content

            logger.info(f"LLM response generated ({len(result)} chars)")
            return result

        except Exception as e:
            logger.error(f"LLM generation failed: {e}", exc_info=True)
            raise

    def chat_with_context(
        self,
        user_message: str,
        system_prompt: str,
        conversation_history: Optional[list] = None,
    ) -> str:
        """
        Chat with LLM while maintaining conversation context.

        Args:
            user_message: Message from user
            system_prompt: System prompt to define bot behavior
            conversation_history: Previous chat messages. Format: [{"role": "user"|"assistant", "content": "..."}, ...]

        Returns:
            Response from LLM
        """
        try:
            messages = []

            messages.append(SystemMessage(content=system_prompt))

            if conversation_history:
                for msg in conversation_history:
                    if msg["role"] == "user":
                        messages.append(HumanMessage(content=msg["content"]))
                    elif msg["role"] == "assistant":
                        messages.append(AIMessage(content=msg["content"]))

            messages.append(HumanMessage(content=user_message))

            response = self.llm.invoke(messages)
            result = response.content

            logger.info("Chat response generated")
            return result

        except Exception as e:
            logger.error(f"Chat context failed: {e}", exc_info=True)
            raise
