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

- ACE-Step batch directories containing FLAC recordings and source metadata.
- `audio_story_registry.json`: story descriptions drawn from recorded batch narratives.
- `audio_narrative_catalog.json`: generated story, scene, and recording index.
- `build_audio_catalog.py`: catalog builder and validator.

## Publication workflow

After successful recording archival, `kaggle_runner.py` launches the shared Git AUTO dispatcher using the canonical archive path. The dispatcher identifies the registered source and routes the request through `backup.publish_repository`. Archive policy handles in-place Git additions, revisions, safety checks, locking, resumable publication, and remote verification. Scheduled planned publication uses the same Archive policy through Nightjet.

The former separate checkout under `/Users/kugel/Sites/mushroom-audio-narrative-library/` is not the Git repository. The former `audio_archive_git_sync.py` workflow is no longer called by the runner; retirement of legacy files is a separate dependency-checked task.

## Verified state and remaining checks

- Git history and the configured SSH remote were preserved when `.git` moved into the canonical archive.
- The central registry points `source_path` and `local_repository` to that archive.
- Universal AUTO routing and Archive integration tests passed (44 tests, 13 November 2026).
- The canonical catalog was rebuilt with 14 stories and 552 recordings, preserving all 472 previously cataloged recordings.
- The first central AUTO publication is **REMOTE_VERIFIED**: local `main` and GitHub `main` both equal `e2cefd1e2927a424068016abc19398a20c4acfd0`; the working tree was clean.
- Eight previously unpublished audio batches were included. The canonical catalog contains 14 stories and 552 recordings.
- The separate public Audio Player retains 38 additional legacy recordings: 18 stories and 590 recordings, published through `vspace_publisher.py --update`.
- The publisher reported **LIVE VERIFIED** at `https://vspace-agent.github.io/mushroom-audio-player/`.
- This FLAC-backed public player is separate from the older MP3 Audio Evaluation inventory.

An AUTO event requests publication but does not itself prove that GitHub was updated. A successful Archive remote-verification result is required before reporting publication complete.
