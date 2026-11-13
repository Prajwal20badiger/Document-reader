import json
import re
from typing import Dict, Any, Optional
import httpx
from pydantic import ValidationError
from app.config import settings
from app.schemas.document import DocumentAnalyzeResponse, GlossaryItem

class AIServiceException(Exception):
    def __init__(self, code: str, message: str, suggestion: str = ""):
        super().__init__(message)
        self.code = code
        self.message = message
        self.suggestion = suggestion

class AIService:
    SYSTEM_PROMPT = """You are an expert document simplifier. Your task is to analyze complex, dense, or technical documents and rewrite them into plain, easy-to-understand language while preserving 100% of the factual accuracy, numerical figures, dates, obligations, and safety warnings.

Guidelines:
1. Do not invent facts, extrapolate unsupported conclusions, or fabricate data.
2. Preserve exact names, dates, quantities, units, conditions, exceptions, and warnings.
3. If information is ambiguous in the source, explicitly mention the ambiguity rather than guessing.
4. Keep the simplified text faithful to the original scope and meaning.
5. Provide:
   - summary: A concise, plain-language executive overview (2-4 sentences).
   - simplified_text: A comprehensive, easy-to-read version of the document.
   - key_points: A list of 3-7 key actionable takeaways or critical facts.
   - glossary: A list of objects with 'term' and 'definition' explaining complex or technical terms in simple language.
6. Return ONLY a valid JSON object matching this schema:
{
  "summary": "...",
  "simplified_text": "...",
  "key_points": ["point 1", "point 2"],
  "glossary": [
    {"term": "Example", "definition": "A clear, plain explanation."}
  ]
}
"""

    def is_configured(self, custom_key: Optional[str] = None) -> bool:
        """
        Checks whether an AI API key is configured either globally or per-request.
        """
        key = custom_key or settings.AI_API_KEY
        return bool(key and key.strip())

    async def analyze_document(
        self,
        text: str,
        document_name: str,
        extraction_method: str,
        custom_key: Optional[str] = None,
        custom_model: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Sends extracted document text to the LLM and validates the structured output.
        """
        api_key = (custom_key or settings.AI_API_KEY).strip()
        model = (custom_model or settings.AI_MODEL).strip()

        if not api_key:
            raise AIServiceException(
                code="AI_UNAVAILABLE",
                message="AI service credentials are not configured.",
                suggestion="Please configure AI_API_KEY in the backend .env or provide an API key in the UI settings."
            )

        # Truncate text if excessively long to bound cost and latency (e.g. 30,000 chars)
        max_chars = 30000
        bounded_text = text[:max_chars]

        user_content = (
            f"Please analyze and simplify the following extracted document text from '{document_name}':\n\n"
            f"```\n{bounded_text}\n```"
        )

        raw_response_text = await self._call_llm(api_key, model, user_content)
        parsed_data = self._parse_and_validate_json(raw_response_text)
        return parsed_data

    async def _call_llm(self, api_key: str, model: str, user_content: str) -> str:
        """
        Dispatches request to either Gemini API or OpenAI-compatible endpoint.
        """
        # Determine provider based on key format or model name
        is_gemini = api_key.startswith("AIza") or "gemini" in model.lower()

        if is_gemini:
            return await self._call_gemini(api_key, model, user_content)
        else:
            return await self._call_openai(api_key, model, user_content)

    async def _call_gemini(self, api_key: str, model: str, user_content: str) -> str:
        # Normalize model name for Google API
        model_name = model if "/" not in model else model.split("/")[-1]
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{model_name}:generateContent?key={api_key}"

        payload = {
            "systemInstruction": {
                "parts": [{"text": self.SYSTEM_PROMPT}]
            },
            "contents": [
                {
                    "role": "user",
                    "parts": [{"text": user_content}]
                }
            ],
            "generationConfig": {
                "responseMimeType": "application/json",
                "temperature": 0.2
            }
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                resp = await client.post(url, json=payload)
            except httpx.TimeoutException:
                raise AIServiceException(
                    code="AI_TIMEOUT",
                    message="The AI analysis service timed out after 45 seconds.",
                    suggestion="Please try again or submit a shorter document."
                )
            except Exception as e:
                raise AIServiceException(
                    code="AI_NETWORK_ERROR",
                    message=f"Failed to reach AI service: {str(e)}",
                    suggestion="Check server network connection and API endpoint availability."
                )

        if resp.status_code != 200:
            error_msg = resp.text
            try:
                err_data = resp.json()
                if "error" in err_data and "message" in err_data["error"]:
                    error_msg = err_data["error"]["message"]
            except Exception:
                pass

            if resp.status_code == 400:
                raise AIServiceException(
                    code="AI_BAD_REQUEST",
                    message=f"AI provider rejected the request: {error_msg}",
                    suggestion="Verify the model name and document format."
                )
            elif resp.status_code in (401, 403):
                raise AIServiceException(
                    code="AI_AUTH_FAILED",
                    message=f"AI authentication failed: {error_msg}",
                    suggestion="Please check that your API key is valid and has sufficient permissions."
                )
            elif resp.status_code == 429:
                raise AIServiceException(
                    code="AI_RATE_LIMIT",
                    message="AI provider rate limit reached.",
                    suggestion="Please wait a moment before retrying."
                )
            else:
                raise AIServiceException(
                    code="AI_PROVIDER_ERROR",
                    message=f"AI provider returned HTTP {resp.status_code}: {error_msg}",
                    suggestion="Please try again later or check your AI provider status."
                )

        data = resp.json()
        try:
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError) as e:
            raise AIServiceException(
                code="AI_INVALID_RESPONSE",
                message="AI provider returned an unexpected response structure.",
                suggestion="Please try again."
            )

    async def _call_openai(self, api_key: str, model: str, user_content: str) -> str:
        url = "https://api.openai.com/v1/chat/completions"
        headers = {
            "Authorization": f"Bearer {api_key}",
            "Content-Type": "application/json"
        }
        payload = {
            "model": model,
            "messages": [
                {"role": "system", "content": self.SYSTEM_PROMPT},
                {"role": "user", "content": user_content}
            ],
            "response_format": {"type": "json_object"},
            "temperature": 0.2
        }

        async with httpx.AsyncClient(timeout=45.0) as client:
            try:
                resp = await client.post(url, headers=headers, json=payload)
            except httpx.TimeoutException:
                raise AIServiceException(
                    code="AI_TIMEOUT",
                    message="The AI analysis service timed out after 45 seconds.",
                    suggestion="Please try again or submit a shorter document."
                )
            except Exception as e:
                raise AIServiceException(
                    code="AI_NETWORK_ERROR",
                    message=f"Failed to reach AI service: {str(e)}",
                    suggestion="Check server network connection and API endpoint availability."
                )

        if resp.status_code != 200:
            error_msg = resp.text
            try:
                err_data = resp.json()
                if "error" in err_data and "message" in err_data["error"]:
                    error_msg = err_data["error"]["message"]
            except Exception:
                pass
            raise AIServiceException(
                code="AI_PROVIDER_ERROR",
                message=f"AI service error ({resp.status_code}): {error_msg}",
                suggestion="Verify your API credentials and model quota."
            )

        data = resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError):
            raise AIServiceException(
                code="AI_INVALID_RESPONSE",
                message="AI provider returned an unexpected payload structure.",
                suggestion="Please try again."
            )

    def _parse_and_validate_json(self, raw_text: str) -> Dict[str, Any]:
        """
        Strips optional markdown fences and validates required fields.
        """
        clean_text = raw_text.strip()
        # Strip ```json ... ``` markdown code blocks if present
        if clean_text.startswith("```"):
            clean_text = re.sub(r"^```(?:json)?\s*", "", clean_text)
            clean_text = re.sub(r"\s*```$", "", clean_text)
            clean_text = clean_text.strip()

        try:
            parsed = json.loads(clean_text)
        except json.JSONDecodeError as e:
            raise AIServiceException(
                code="AI_MALFORMED_JSON",
                message=f"AI response was not valid JSON: {str(e)}",
                suggestion="Server received a non-JSON response from the AI model."
            )

        if not isinstance(parsed, dict):
            raise AIServiceException(
                code="AI_INVALID_SCHEMA",
                message="AI response must be a JSON object.",
                suggestion="Invalid response structure."
            )

        # Enforce required fields
        required_keys = ["summary", "simplified_text", "key_points", "glossary"]
        for key in required_keys:
            if key not in parsed:
                raise AIServiceException(
                    code="AI_INVALID_SCHEMA",
                    message=f"AI response missing required field: '{key}'.",
                    suggestion="The AI response did not fulfill the required contract schema."
                )

        # Normalize key_points
        if not isinstance(parsed["key_points"], list):
            parsed["key_points"] = [str(parsed["key_points"])]

        # Normalize glossary items
        normalized_glossary = []
        if isinstance(parsed["glossary"], list):
            for item in parsed["glossary"]:
                if isinstance(item, dict) and "term" in item and "definition" in item:
                    normalized_glossary.append({
                        "term": str(item["term"]),
                        "definition": str(item["definition"])
                    })
        parsed["glossary"] = normalized_glossary

        return parsed

ai_service = AIService()
