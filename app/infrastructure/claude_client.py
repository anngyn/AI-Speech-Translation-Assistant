from __future__ import annotations

import asyncio
import json
import os

from dotenv import load_dotenv

from app.domain.entities import TranslationResult
from app.domain.glossary import glossary_prompt_fragment


DEFAULT_MODEL = "global.anthropic.claude-haiku-4-5-20251001-v1:0"


class ClaudeClient:
    def __init__(self, model: str = DEFAULT_MODEL, runtime_client=None) -> None:
        load_dotenv()
        if runtime_client is None:
            import boto3

            runtime_client = boto3.client(
                "bedrock-runtime",
                region_name=os.getenv("AWS_REGION") or os.getenv("AWS_DEFAULT_REGION"),
            )
        self.client = runtime_client
        self.model = os.getenv("BEDROCK_CLAUDE_MODEL_ID") or os.getenv("BEDROCK_CLAUDE_MODEL", model)

    async def translate(
        self,
        text: str,
        source_language: str,
        target_language: str,
        entity_memory,
    ) -> TranslationResult:
        if not text.strip():
            return TranslationResult(source_language=source_language, target_language=target_language)

        system_prompt = build_system_prompt(source_language, target_language, entity_memory)
        try:
            response = await asyncio.to_thread(
                self.client.invoke_model,
                modelId=self.model,
                body=json.dumps(
                    {
                        "anthropic_version": "bedrock-2023-05-31",
                        "max_tokens": 800,
                        "temperature": 0,
                        "system": system_prompt,
                        "messages": [{"role": "user", "content": text}],
                    }
                ),
                contentType="application/json",
                accept="application/json",
            )
            payload = json.loads(response["body"].read())
            translated = "".join(
                block.get("text", "") for block in payload.get("content", []) if block.get("type") == "text"
            ).strip()
            usage = payload.get("usage", {})
            return TranslationResult(
                translated=translated,
                source_language=source_language,
                target_language=target_language,
                input_tokens=int(usage.get("input_tokens", 0) or 0),
                output_tokens=int(usage.get("output_tokens", 0) or 0),
            )
        except Exception as exc:  # noqa: BLE001 - provider boundary returns structured errors
            return TranslationResult(
                source_language=source_language,
                target_language=target_language,
                error=f"bedrock_claude_error: {exc}",
            )


def build_system_prompt(source_language: str, target_language: str, entity_memory) -> str:
    return (
        "You are a professional interpreter for OnPoint, a Vietnamese e-commerce company.\n"
        f"Translate {source_language} to {target_language}.\n"
        "Preserve exactly: numbers, dates, amounts, proper nouns.\n"
        f"Do not translate these terms: {glossary_prompt_fragment()}.\n"
        f"Known entities this session: {entity_memory.to_prompt_fragment()}.\n"
        "Return only the translated text. No explanation."
    )
