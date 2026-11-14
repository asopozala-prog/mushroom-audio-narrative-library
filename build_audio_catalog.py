# Build a portable Audio Narrative catalog from canonical ACE-Step batch metadata.
import argparse
import hashlib
import json
import os
import tempfile
import re
from pathlib import Path
from urllib.parse import quote

ARCHIVE = Path(__file__).resolve().parent
SCHEMA = "mushroom.audio-narrative.catalog"
VERSION = 1
MODELS = {"turbo": "ACE-Step 1.5 · Turbo", "sft_lm": "ACE-Step 1.5 · LM+SFT"}


def build(archive, audio_base):
    # The catalog itself preserves editorial descriptions and legacy recordings.
    catalog_path = archive / "audio_narrative_catalog.json"
    if catalog_path.is_file():
        catalog = json.loads(catalog_path.read_text(encoding="utf-8"))
        if catalog.get("schema") != SCHEMA or catalog.get("schema_version") != VERSION:
            raise ValueError("Unsupported existing catalog")
        groups = {}
        seen_recordings = set()
        seen_scenes = set()
        for story in catalog["stories"]:
            if story["id"] in groups:
                raise ValueError(f"Duplicate existing story: {story['id']}")
            for scene in story["scenes"]:
                if scene["id"] in seen_scenes:
                    raise ValueError(f"Duplicate existing scene: {scene['id']}")
                seen_scenes.add(scene["id"])
                for recording in scene["recordings"]:
                    if recording["id"] in seen_recordings:
                        raise ValueError(f"Duplicate existing recording: {recording['id']}")
                    seen_recordings.add(recording["id"])
            groups[story["id"]] = {
                **story, "scenes": {scene["id"]: scene for scene in story["scenes"]}
            }
    else:
        groups = {}
        seen_recordings = set()

    for batch_path in sorted(archive.glob("studio_batch_*/batch.json")):
        folder = batch_path.parent
        report_path = folder / "experiment.json"
        if not report_path.is_file():
            continue
        batch = json.loads(batch_path.read_text(encoding="utf-8"))
        theme = batch.get("batch_theme")
        if not theme:
            continue
        report = json.loads(report_path.read_text(encoding="utf-8"))
        if report.get("batch_id") != folder.name:
            raise ValueError(f"Batch identity mismatch: {folder}")
        route = batch["route"]
        if route not in MODELS:
            raise ValueError(f"Unknown model route: {route}")
        prompts = {p["output_name"]: p for p in batch["prompts"]}
        if len(prompts) != len(batch["prompts"]):
            raise ValueError(f"Duplicate prompt names: {folder}")
        if theme not in groups:
            narrative = next(
                (p["prompt"].strip() for p in batch["prompts"]
                 if p["output_name"] == "track_01_batch_story"),
                "",
            )
            groups[theme] = {
                "id": theme,
                "title": theme.replace("_", " ").title(),
                "description": narrative,
                "scenes": {},
            }
        story = groups[theme]
        normalized = []
        for output in report.get("outputs", []):
            if "composition" in output:
                normalized.append((output["composition"], int(output["variation"]), output["relative_path"]))
            elif "output_name" in output and isinstance(output.get("files"), list):
                normalized.extend(
                    (output["output_name"], index, relative)
                    for index, relative in enumerate(output["files"], 1)
                )
            else:
                raise ValueError(f"Unknown recording format: {folder}")
        for name, variation, relative in normalized:
            if name not in prompts:
                raise ValueError(f"Recording lacks prompt: {folder}/{name}")
            source = (folder / relative).resolve()
            if not source.is_relative_to(folder.resolve()) or not source.is_file():
                raise ValueError(f"Invalid recording path: {source}")
            prompt = prompts[name]["prompt"]
            prompt_key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
            scene_id = f"{theme}/{name}/{prompt_key}"
            scene = story["scenes"].setdefault(scene_id, {
                "id": scene_id,
                "title": name.replace("_", " ").title(),
                "order": len(story["scenes"]) + 1,
                "prompt": prompt,
                "recordings": [],
            })
            if scene["prompt"] != prompt:
                raise ValueError(f"Conflicting scene prompt: {scene_id}")
            recording_id = f"{folder.name}/{name}/{variation}"
            if recording_id in seen_recordings:
                continue
            seen_recordings.add(recording_id)
            relative_url = "/".join(quote(part) for part in source.relative_to(archive).parts)
            audio_url = audio_base.rstrip("/") + "/" + relative_url if audio_base else relative_url
            scene["recordings"].append({
                "id": recording_id,
                "model": MODELS[route],
                "timestamp": batch["generation_started_at"],
                "audio": {"format": "flac", "url": audio_url},
                "downloads": [{"format": "flac", "url": audio_url}],
                "filename": source.stem,
            })
    result = []
    for story in groups.values():
        result.append({**story, "scenes": list(story["scenes"].values())})
    return {"schema": SCHEMA, "schema_version": VERSION, "stories": result}


def main():
    parser = argparse.ArgumentParser(description="Generate a portable Audio Narrative JSON catalog")
    parser.add_argument("--archive", type=Path, default=ARCHIVE)
    parser.add_argument("--audio-base", default="", help="Optional public URL prefix for archive recordings")
    parser.add_argument("--output", type=Path, help="Write catalog JSON to this path")
    args = parser.parse_args()
    catalog = build(args.archive.resolve(), args.audio_base)
    counts = (len(catalog["stories"]),
              sum(len(story["scenes"]) for story in catalog["stories"]),
              sum(len(scene["recordings"]) for story in catalog["stories"] for scene in story["scenes"]))
    if args.output:
        args.output.parent.mkdir(parents=True, exist_ok=True)
        fd, temporary = tempfile.mkstemp(
            prefix=".audio_catalog_", suffix=".tmp", dir=args.output.parent
        )
        try:
            with os.fdopen(fd, "w", encoding="utf-8") as handle:
                handle.write(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
                handle.flush()
                os.fsync(handle.fileno())
            os.replace(temporary, args.output)
        finally:
            if os.path.exists(temporary):
                os.unlink(temporary)
    print("SCHEMA:", catalog["schema"], catalog["schema_version"])
    print("STORIES / SCENES / RECORDINGS:", *counts)
    print("AUDIO BASE:", args.audio_base or "(catalog-relative; requires matching hosted audio paths)")
    print("OUTPUT:", args.output or "(validation only)")


if __name__ == "__main__":
    main()
