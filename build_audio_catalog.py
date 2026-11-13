# Build a portable Audio Narrative catalog from canonical ACE-Step batch metadata.
import argparse
import hashlib
import json
import re
from pathlib import Path
from urllib.parse import quote

ARCHIVE = Path(__file__).resolve().parent
SCHEMA = "mushroom.audio-narrative.catalog"
VERSION = 1
MODELS = {"turbo": "ACE-Step 1.5 · Turbo", "sft_lm": "ACE-Step 1.5 · LM+SFT"}


def build(archive, audio_base):
    stories = json.loads((archive / "audio_story_registry.json").read_text())
    if not isinstance(stories, dict):
        raise ValueError("Story registry must be an object")
    groups = {}
    seen_recordings = set()
    for batch_path in sorted(archive.glob("studio_batch_*/batch.json")):
        folder = batch_path.parent
        report_path = folder / "experiment.json"
        if not report_path.is_file():
            continue
        batch = json.loads(batch_path.read_text())
        theme = batch.get("batch_theme")
        if not theme:
            continue
        if theme not in stories:
            raise ValueError(f"Missing canonical story: {theme}")
        report = json.loads(report_path.read_text())
        if report.get("batch_id") != folder.name:
            raise ValueError(f"Batch identity mismatch: {folder}")
        route = batch["route"]
        if route not in MODELS:
            raise ValueError(f"Unknown model route: {route}")
        prompts = {p["output_name"]: p for p in batch["prompts"]}
        if len(prompts) != len(batch["prompts"]):
            raise ValueError(f"Duplicate prompt names: {folder}")
        story = groups.setdefault(theme, {
            "id": theme, "title": theme.replace("_", " ").title(),
            "description": stories[theme], "scenes": {}
        })
        normalized = []
        for output in report.get("outputs", []):
            if "composition" in output:
                normalized.append((output["composition"], int(output["variation"]), output["relative_path"]))
            elif "output_name" in output and isinstance(output.get("files"), list):
                normalized.extend((output["output_name"], index, relative)
                                  for index, relative in enumerate(output["files"], 1))
            else:
                raise ValueError(f"Unknown recording format: {folder}")
        for name, variation, relative in normalized:
            if name not in prompts:
                raise ValueError(f"Recording lacks prompt: {folder}/{name}")
            source = (folder / relative).resolve()
            if not source.is_relative_to(folder.resolve()) or not source.is_file():
                raise ValueError(f"Invalid recording path: {source}")
            prompt = prompts[name]["prompt"]
            # A reused composition name with a different prompt is a distinct scene.
            # Identical prompts from multiple batches share one scene and retain all versions.
            prompt_key = hashlib.sha256(prompt.encode("utf-8")).hexdigest()[:16]
            scene_id = f"{theme}/{name}/{prompt_key}"
            scene = story["scenes"].setdefault(scene_id, {
                "id": scene_id, "title": name.replace("_", " ").title(),
                "order": len(story["scenes"]) + 1, "prompt": prompt, "recordings": []
            })
            recording_id = f"{folder.name}/{name}/{variation}"
            if recording_id in seen_recordings:
                raise ValueError(f"Duplicate recording: {recording_id}")
            seen_recordings.add(recording_id)
            # Relative paths resolve against the catalog URL, or against an explicit audio_base URL.
            relative_url = "/".join(quote(part) for part in source.relative_to(archive).parts)
            audio_url = audio_base.rstrip("/") + "/" + relative_url if audio_base else relative_url
            scene["recordings"].append({
                "id": recording_id, "model": MODELS[route],
                "timestamp": batch["generation_started_at"],
                "audio": {"format": "flac", "url": audio_url},
                "downloads": [{"format": "flac", "url": audio_url}],
                "filename": source.stem
            })
    if set(groups) != set(stories):
        raise ValueError(f"Stories without batches: {sorted(set(stories) - set(groups))}")
    result = []
    for story in groups.values():
        story["scenes"] = list(story["scenes"].values())
        result.append(story)
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
        args.output.write_text(json.dumps(catalog, ensure_ascii=False, indent=2) + "\n")
    print("SCHEMA:", catalog["schema"], catalog["schema_version"])
    print("STORIES / SCENES / RECORDINGS:", *counts)
    print("AUDIO BASE:", args.audio_base or "(catalog-relative; requires matching hosted audio paths)")
    print("OUTPUT:", args.output or "(validation only)")


if __name__ == "__main__":
    main()
