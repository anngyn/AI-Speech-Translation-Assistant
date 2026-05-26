from __future__ import annotations

import argparse
import asyncio
import json
import re
import sys
import time
from pathlib import Path

from jiwer import wer

ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

from app.application.interpret_session import InterpretSession  # noqa: E402
from app.application.session_state import SessionState, LanguageDirection  # noqa: E402
from app.domain.entities import EntityMemory  # noqa: E402
from app.infrastructure.audio_utils import PydubAudioConverter, load_audio_file, slice_audio  # noqa: E402
from app.infrastructure.claude_client import ClaudeClient  # noqa: E402
from app.infrastructure.whisper_client import WhisperClient  # noqa: E402

WHISPER_PER_MINUTE = 0.006
HAIKU_INPUT_PER_TOKEN = 0.25 / 1_000_000
HAIKU_OUTPUT_PER_TOKEN = 1.25 / 1_000_000


async def run(audio_path: Path, ground_truth_path: Path) -> int:
    audio = load_audio_file(audio_path)
    chunks = slice_audio(audio)
    session = SessionState()
    interpreter = InterpretSession(PydubAudioConverter(), WhisperClient(), ClaudeClient())

    originals: list[str] = []
    translations: list[str] = []
    latencies: list[int] = []
    empty_chunks = 0
    audio_seconds = 0.0
    input_tokens = 0
    output_tokens = 0

    wall_start = time.perf_counter()
    for chunk in chunks:
        result = await interpreter.process_audio_chunk(session, chunk)
        if result.is_silent:
            empty_chunks += 1
            continue
        if result.original:
            originals.append(result.original)
        if result.translated:
            translations.append(result.translated)
        latencies.append(result.latency_ms)
        audio_seconds += float(result.cost.get("audio_seconds", 0) or 0)
        input_tokens += int(result.cost.get("input_tokens", 0) or 0)
        output_tokens += int(result.cost.get("output_tokens", 0) or 0)

    ground_truth = ground_truth_path.read_text(encoding="utf-8")
    transcript = " ".join(originals)
    stt_wer = wer(ground_truth, transcript) * 100
    entity_rate = entity_preservation_rate(session.entity_memory, " ".join(translations))
    avg_latency = sum(latencies) / len(latencies) / 1000 if latencies else 0
    max_latency = max(latencies) / 1000 if latencies else 0
    whisper_cost = (audio_seconds / 60) * WHISPER_PER_MINUTE
    claude_cost = input_tokens * HAIKU_INPUT_PER_TOKEN + output_tokens * HAIKU_OUTPUT_PER_TOKEN
    total_cost = whisper_cost + claude_cost
    projected_2h = total_cost * ((120 * 60) / max(audio_seconds, 1))

    print("=== AI Interpreter Evaluation Report ===")
    print(f"Audio file   : {audio_path.name}")
    print(f"Duration     : {format_duration(len(audio))}")
    print()
    print("STT")
    print(f"  WER                  : {stt_wer:.1f}% {'PASS' if stt_wer < 10 else 'FAIL'}")
    print(f"  Chunks processed     : {len(chunks)}")
    print(f"  Empty chunks skipped : {empty_chunks}")
    print()
    print("Translation")
    print(f"  Entity preservation  : {entity_rate:.1f}% {'PASS' if entity_rate > 95 else 'FAIL'}")
    print(f"  Avg latency          : {avg_latency:.2f}s {'PASS' if avg_latency < 3 else 'FAIL'}")
    print(f"  Max latency          : {max_latency:.2f}s")
    print()
    print("Cost")
    print(f"  Whisper              : ${whisper_cost:.3f}")
    print(f"  Bedrock Claude Haiku : ${claude_cost:.3f}")
    print(f"  Total                : ${total_cost:.3f}")
    print(f"  Projected 2h session : ${projected_2h:.2f} {'PASS' if projected_2h < 50 else 'FAIL'}")
    print(f"  Wall-clock runtime   : {time.perf_counter() - wall_start:.1f}s")

    return 0 if stt_wer < 10 and entity_rate > 95 and avg_latency < 3 and projected_2h < 50 else 1


async def run_manifest(manifest_path: Path, limit: int | None = None) -> int:
    manifest_dir = manifest_path.parent
    entries = [json.loads(line) for line in manifest_path.read_text(encoding="utf-8").splitlines() if line.strip()]
    if limit is not None:
        entries = entries[:limit]

    session = SessionState()
    session.set_direction(LanguageDirection.EN_VI.value)
    interpreter = InterpretSession(PydubAudioConverter(), WhisperClient(), ClaudeClient())

    refs: list[str] = []
    hyps: list[str] = []
    translations: list[str] = []
    latencies: list[int] = []
    empty_chunks = 0
    audio_seconds = 0.0
    input_tokens = 0
    output_tokens = 0
    errors: list[str] = []

    wall_start = time.perf_counter()
    for entry in entries:
        audio_file = manifest_dir / entry["audio"]
        chunks = slice_audio(load_audio_file(audio_file))
        refs.append(entry["transcript_en"])

        for chunk_bytes in chunks:
            result = await interpreter.process_audio_chunk(session, chunk_bytes)
            if result.error:
                errors.append(f"{entry['id']}: {result.error}")
                continue
            if result.is_silent:
                empty_chunks += 1
                continue
            if result.original:
                hyps.append(result.original)
            if result.translated:
                translations.append(result.translated)
            latencies.append(result.latency_ms)
            audio_seconds += float(result.cost.get("audio_seconds", 0) or 0)
            input_tokens += int(result.cost.get("input_tokens", 0) or 0)
            output_tokens += int(result.cost.get("output_tokens", 0) or 0)

    transcript = " ".join(hyps)
    ground_truth = " ".join(refs)
    stt_wer = wer(ground_truth, transcript) * 100 if hyps else 0.0
    entity_rate = entity_preservation_rate(session.entity_memory, " ".join(translations))
    avg_latency = sum(latencies) / len(latencies) / 1000 if latencies else 0
    max_latency = max(latencies) / 1000 if latencies else 0
    whisper_cost = (audio_seconds / 60) * WHISPER_PER_MINUTE
    claude_cost = input_tokens * HAIKU_INPUT_PER_TOKEN + output_tokens * HAIKU_OUTPUT_PER_TOKEN
    total_cost = whisper_cost + claude_cost
    projected_2h = total_cost * ((120 * 60) / max(audio_seconds, 1))

    print("=== AI Interpreter Evaluation Report (manifest) ===")
    print(f"Manifest     : {manifest_path}")
    print(f"Entries      : {len(entries)}")
    print()
    print("STT")
    print(f"  WER                  : {stt_wer:.1f}% {'PASS' if stt_wer < 10 else 'FAIL'}")
    print(f"  Chunks transcribed   : {len(hyps)}, silent: {empty_chunks}")
    print(f"  Silent skipped       : {empty_chunks}")
    print()
    print("Translation")
    print(f"  Entity preservation  : {entity_rate:.1f}% {'PASS' if entity_rate > 95 else 'FAIL'}")
    print(f"  Avg latency          : {avg_latency:.2f}s {'PASS' if avg_latency < 3 else 'FAIL'}")
    print(f"  Max latency          : {max_latency:.2f}s")
    print()
    print("Cost")
    print(f"  Whisper              : ${whisper_cost:.3f}")
    print(f"  Bedrock Claude Haiku : ${claude_cost:.3f}")
    print(f"  Total                : ${total_cost:.3f}")
    print(f"  Projected 2h session : ${projected_2h:.2f} {'PASS' if projected_2h < 50 else 'FAIL'}")
    print(f"  Wall-clock runtime   : {time.perf_counter() - wall_start:.1f}s")
    if errors:
        print()
        print(f"Errors ({len(errors)}):")
        for err in errors:
            print(f"  {err}")

    return 0 if stt_wer < 10 and entity_rate > 95 and avg_latency < 3 and projected_2h < 50 else 1


def entity_preservation_rate(memory: EntityMemory, translated_text: str) -> float:
    entities = [entity for entity in memory.all_entities() if entity and re.search(r"\d|[A-Z]", entity)]
    if not entities:
        return 100.0
    hits = sum(1 for entity in entities if entity in translated_text)
    return hits / len(entities) * 100


def format_duration(milliseconds: int) -> str:
    total_seconds = round(milliseconds / 1000)
    minutes, seconds = divmod(total_seconds, 60)
    return f"{minutes}m {seconds:02d}s"


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="Run AI interpreter evaluation.")
    mode = parser.add_mutually_exclusive_group(required=True)
    mode.add_argument("--audio", type=Path, help="Single audio file (use with --ground-truth)")
    mode.add_argument("--manifest", type=Path, help="manifest.jsonl for pre-segmented dataset")
    parser.add_argument("--ground-truth", type=Path, help="Ground-truth text file (required with --audio)")
    parser.add_argument("--limit", type=int, default=None, help="Process only first N entries (manifest mode)")
    return parser.parse_args()


if __name__ == "__main__":
    args = parse_args()
    if args.manifest:
        raise SystemExit(asyncio.run(run_manifest(args.manifest, limit=args.limit)))
    if not args.ground_truth:
        raise SystemError("--ground-truth required when using --audio")
    raise SystemExit(asyncio.run(run(args.audio, args.ground_truth)))
