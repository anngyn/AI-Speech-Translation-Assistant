from __future__ import annotations

import json
import os
from io import BytesIO
from pathlib import Path

import soundfile as sf
from datasets import Audio, load_dataset
from dotenv import load_dotenv
from huggingface_hub import HfApi, hf_hub_download, list_repo_files


REPO_ID = "vinai/PhoST"
SPLIT = "train"
N = 30
OUT = Path("tests/fixtures/phost-mini")
AUDIO_DIR = OUT / "audio"


def token() -> str | None:
    return os.getenv("HF_TOKEN") or os.getenv("HUGGINGFACE_HUB_TOKEN")


def split_text_files(files: list[str]) -> list[str]:
    split_prefix = f"text_data/{SPLIT}/"
    return [
        path
        for path in files
        if path.startswith(split_prefix) and path.lower().endswith((".en", ".vi"))
    ]


def discover_text_files(hf_token: str | None) -> list[str]:
    files = split_text_files(list_repo_files(REPO_ID, repo_type="dataset", token=hf_token))
    if files:
        return files

    tree = HfApi().list_repo_tree(
        REPO_ID,
        path_in_repo="text_data",
        repo_type="dataset",
        recursive=True,
        token=hf_token,
    )
    return split_text_files([item.path for item in tree])


def text_id(repo_file: str) -> str:
    return Path(repo_file).stem


def load_text_index(hf_token: str | None) -> dict[str, tuple[str, str]]:
    files = discover_text_files(hf_token)
    if not files:
        raise FileNotFoundError(f"Khong thay text_data cho split={SPLIT}")
    print("text files:", files[:10])

    en_files = {text_id(path): path for path in files if path.endswith(".en")}
    vi_files = {text_id(path): path for path in files if path.endswith(".vi")}
    return {
        item_id: (en_files[item_id], vi_files[item_id])
        for item_id in en_files.keys() & vi_files.keys()
    }


def read_lines(repo_file: str, hf_token: str | None) -> list[str]:
    path = hf_hub_download(
        REPO_ID,
        repo_file,
        repo_type="dataset",
        token=hf_token,
    )
    return Path(path).read_text(encoding="utf-8").splitlines()


def load_text_pair(
    item_id: str,
    text_index: dict[str, tuple[str, str]],
    hf_token: str | None,
) -> dict[str, object]:
    if item_id not in text_index:
        raise KeyError(f"Khong thay text cho audio id={item_id}")

    en_file, vi_file = text_index[item_id]
    en_lines = [line.strip() for line in read_lines(en_file, hf_token) if line.strip()]
    vi_lines = [line.strip() for line in read_lines(vi_file, hf_token) if line.strip()]
    return {
        "transcript_en": " ".join(en_lines),
        "translation_vi": " ".join(vi_lines),
        "segments_en": len(en_lines),
        "segments_vi": len(vi_lines),
    }


def hf_audio_path(path: str) -> str | None:
    marker = f"hf://datasets/{REPO_ID}@"
    if not path.startswith(marker):
        return None
    _, repo_path = path[len(marker):].split("/", 1)
    return repo_path


def audio_id(audio: dict) -> str:
    path = audio.get("path") or ""
    repo_path = hf_audio_path(path) or path
    return Path(repo_path).stem


def decode_audio(audio: dict, hf_token: str | None) -> tuple[object, int]:
    if "array" in audio:
        return audio["array"], audio["sampling_rate"]
    if audio.get("bytes") is not None:
        return sf.read(BytesIO(audio["bytes"]))
    if audio.get("path") is not None:
        audio_path = audio["path"]
        repo_path = hf_audio_path(audio_path)
        if repo_path is not None:
            audio_path = hf_hub_download(
                REPO_ID,
                repo_path,
                repo_type="dataset",
                token=hf_token,
            )
        return sf.read(audio_path)
    raise ValueError(f"Khong doc duoc audio object: keys={list(audio.keys())}")


load_dotenv()
hf_token = token()
AUDIO_DIR.mkdir(parents=True, exist_ok=True)
text_index = load_text_index(hf_token)

ds = load_dataset(
    REPO_ID,
    split=SPLIT,
    streaming=True,
    token=hf_token,
)
ds = ds.cast_column("audio", Audio(decode=False))

manifest = []

for i, ex in enumerate(ds):
    if i >= N:
        break
    if i == 0:
        print("columns:", ex.keys())

    if "audio" not in ex:
        raise KeyError(f"Khong thay cot audio. Columns = {list(ex.keys())}")

    item_id = audio_id(ex["audio"])
    wav_path = AUDIO_DIR / f"{i:04d}.wav"
    samples, sampling_rate = decode_audio(ex["audio"], hf_token)
    sf.write(wav_path, samples, sampling_rate)

    row = load_text_pair(item_id, text_index, hf_token)
    manifest.append(
        {
            "id": f"phost_{item_id}",
            "audio": str(wav_path.relative_to(OUT)),
            "transcript_en": row["transcript_en"],
            "translation_vi": row["translation_vi"],
            "segments_en": row["segments_en"],
            "segments_vi": row["segments_vi"],
        }
    )

with open(OUT / "manifest.jsonl", "w", encoding="utf-8") as f:
    for row in manifest:
        f.write(json.dumps(row, ensure_ascii=False) + "\n")

print(f"Saved {len(manifest)} samples to {OUT}")
