import asyncio
import logging
from typing import TypeVar
from pydantic import BaseModel, ValidationError
from app.config import Settings

T = TypeVar("T", bound=BaseModel)
logger = logging.getLogger(__name__)


class GeminiServiceError(RuntimeError):
    pass


class GeminiService:
    def __init__(self, settings: Settings):
        self.settings = settings
        self._client = None

    def _client_or_raise(self):
        if not self.settings.gemini_api_key:
            raise GeminiServiceError("GEMINI_API_KEY is not configured")
        if not self.settings.gemini_model:
            raise GeminiServiceError("GEMINI_MODEL is not configured")
        if self._client is None:
            from google import genai
            self._client = genai.Client(api_key=self.settings.gemini_api_key)
        return self._client

    async def generate_structured(self, system_instruction: str, prompt: str, response_model: type[T]) -> T:
        client = self._client_or_raise()
        last_error: Exception | None = None
        for attempt in range(3):
            try:
                response = await client.aio.models.generate_content(
                    model=self.settings.gemini_model,
                    contents=prompt,
                    config={"system_instruction": system_instruction, "response_mime_type": "application/json", "response_schema": response_model},
                )
                if response.parsed is not None:
                    return response.parsed if isinstance(response.parsed, response_model) else response_model.model_validate(response.parsed)
                return response_model.model_validate_json(response.text)
            except (ValidationError, ValueError) as exc:
                raise GeminiServiceError("Gemini returned invalid structured output") from exc
            except Exception as exc:
                last_error = exc
                logger.warning("Gemini request failed (attempt %s)", attempt + 1)
                if attempt < 2:
                    await asyncio.sleep(0.4 * (2**attempt))
        raise GeminiServiceError("Gemini request failed after retries") from last_error
