# Mushroom House 🍄 Audio Narrative Library

## Purpose

The canonical ACE-Step recording archive on Kugel is also the single local Git repository for the Audio Narrative Library. Git publication preserves its recordings and narrative metadata in the remote archive. The Audio Evaluation Player is a separate publication system.

## Verified locations

| Component | Location |
| --- | --- |
| Canonical recordings and Git repository | `/Users/kugel/media_library/audio/kaggle_ACE/` |
| Central Git backup registry | `/Users/kugel/Kugel-Automation/backups/git/repositories.json` |
| Universal AUTO event dispatcher | `/Users/kugel/Kugel-Automation/backups/git/watcher.py` |
| Shared publication dispatcher | `/Users/kugel/Kugel-Automation/backups/git/backup.py` |
| Archive publication policy | `/Users/kugel/Kugel-Automation/backups/git/archive.py` |
| ACE-Step output archive runner | `/Users/kugel/🍄MushroomHouseMusicLab/kaggle_ACE_step/kaggle_runner.py` |
| SSH remote | `git@github.com:asopozala-prog/mushroom-audio-narrative-library.git` |
| Branch | `main` |

## Contents

- ACE-Step batch directories containing FLAC recordings and original generation metadata.
- `audio_narrative_catalog.json`: the single canonical index of story identities, descriptions, scenes, prompts, and recordings.
- `build_audio_catalog.py`: validates archived recordings, preserves existing editorial descriptions and legacy entries, and atomically incorporates new batches.
- `audio_story_registry.json`: retired legacy metadata file; no longer used by the catalog builder or Audio Evaluation sync. Preserve until dependency and historical-data retirement checks are complete.

## Publication workflow

For batch generation, `kaggle_runner.py` verifies and archives the FLAC recordings, then rebuilds `audio_narrative_catalog.json` before starting the shared Git AUTO dispatcher. If catalog rebuilding fails, the runner does not start that publication event. The dispatcher uses the canonical archive and registered Archive policy for Git publication and remote verification.

The separate public Audio Player at `https://vspace-agent.github.io/mushroom-audio-player/` loads `audio_narrative_catalog.json` directly from the canonical GitHub archive. Its frontend is separately deployed using `vspace_publisher.py --update`; new recordings do not require republishing the frontend.

The MP3 Audio Evaluation system remains separate. Its synchronization script reads story descriptions from the unified catalog.

## Verified state — 14 November 2026

- Unified catalog: **19 stories, 614 recordings**, including all 38 legacy player-only recordings and the 24 recordings from `the_wind_clears_the_branches_for_winter`.
- All 614 catalog FLAC paths verified locally; prior narrative descriptions preserved; rebuilding is deterministic and idempotent.
- Canonical Git publication: **REMOTE_VERIFIED**, commit `ff52f20885aee554d5efeb50646f3226909cc19f`.
- Audio Player frontend: **LIVE VERIFIED**, commit `f912b18`; configured to read the canonical GitHub catalog.
- Remote catalog independently fetched and verified: 19 stories, 614 recordings.
- The runner's automatic catalog rebuild was connected and syntax-checked; a future live Kaggle batch has not yet exercised the entire new chain end-to-end.
- Previously verified shared Git infrastructure tests: 44 passed on 13 November 2026.

An AUTO event requests publication but does not itself prove that GitHub was updated. A successful Archive remote-verification result is required before reporting publication complete.
