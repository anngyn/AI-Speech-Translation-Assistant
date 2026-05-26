import asyncio
from io import BytesIO
import json
import os

from app.domain.entities import EntityMemory
import app.infrastructure.claude_client as claude_module
from app.infrastructure.claude_client import ClaudeClient, DEFAULT_MODEL


class SuccessfulBedrockRuntime:
    @staticmethod
    def invoke_model(**request):
        body = json.loads(request["body"])
        assert request["modelId"] == DEFAULT_MODEL
        assert body["anthropic_version"] == "bedrock-2023-05-31"
        assert body["messages"][0]["content"] == "Doanh thu dat 150 ty Q1."
        payload = {
            "content": [{"type": "text", "text": "Revenue reached 150 ty in Q1."}],
            "usage": {"input_tokens": 22, "output_tokens": 9},
        }
        return {"body": BytesIO(json.dumps(payload).encode("utf-8"))}


class ErrorBedrockRuntime:
    @staticmethod
    def invoke_model(**request):
        raise RuntimeError("denied")


def run_translate_without_worker_thread(client, text):
    original_to_thread = claude_module.asyncio.to_thread

    async def immediate_call(function, *args, **kwargs):
        return function(*args, **kwargs)

    claude_module.asyncio.to_thread = immediate_call
    try:
        return asyncio.run(client.translate(text, "Vietnamese", "English", EntityMemory()))
    finally:
        claude_module.asyncio.to_thread = original_to_thread


def test_claude_client_invokes_bedrock_messages_contract():
    previous_model = os.environ.get("BEDROCK_CLAUDE_MODEL_ID")
    os.environ["BEDROCK_CLAUDE_MODEL_ID"] = DEFAULT_MODEL
    try:
        client = ClaudeClient(runtime_client=SuccessfulBedrockRuntime())

        result = run_translate_without_worker_thread(client, "Doanh thu dat 150 ty Q1.")
    finally:
        if previous_model is None:
            os.environ.pop("BEDROCK_CLAUDE_MODEL_ID", None)
        else:
            os.environ["BEDROCK_CLAUDE_MODEL_ID"] = previous_model

    assert result.translated == "Revenue reached 150 ty in Q1."
    assert result.input_tokens == 22
    assert result.output_tokens == 9


def test_claude_client_returns_structured_bedrock_errors():
    client = ClaudeClient(runtime_client=ErrorBedrockRuntime())

    result = run_translate_without_worker_thread(client, "text")

    assert result.error == "bedrock_claude_error: denied"
