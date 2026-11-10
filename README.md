# Mushroom House 🍄 Audio Narrative Library

## Purpose

Git-backed archive of ACE-Step FLAC recordings and their narrative metadata. The canonical recording archive remains on Kugel; this repository is a published copy, not the source of truth.

## Locations

| Component | Path |
| --- | --- |
| Canonical archive | `/Users/kugel/media_library/audio/kaggle_ACE/` |
| Local Git checkout | `/Users/kugel/Sites/mushroom-audio-narrative-library/` |
| Synchronization script | `/Users/kugel/🍄MushroomHouseMusicLab/kaggle_ACE_step/audio_archive_git_sync.py` |
| Download/archive runner | `/Users/kugel/🍄MushroomHouseMusicLab/kaggle_ACE_step/kaggle_runner.py` |
| Git remote | `git@github.com:asopozala-prog/mushroom-audio-narrative-library.git` |
| Branch | `main` |

## Contents

- `studio_batch_*/`: copied batch directories containing FLAC recordings and experiment metadata.
- `audio_narrative_catalog.json`: narrative stories, scenes, recording references, and descriptions.
- `audio_story_registry.json`: story registry metadata.

The two JSON inventories are copied from the canonical archive; this synchronization script does not generate or enrich them.

## Publication workflow

After `kaggle_runner.py` archives a downloaded batch, it invokes `audio_archive_git_sync.py`.

The synchronization script:

1. Checks the canonical archive, clean Git checkout, `main` branch, and expected SSH remote.
2. Fetches `origin/main` and requires local `HEAD` to match it.
3. Validates catalog schema and verifies referenced FLAC files exist in the canonical archive.
4. Copies previously unpublished physical batch directories containing `experiment.json` and FLAC files, preserving symlinks.
5. Checks individual FLAC sizes against the GitHub 100 MB file limit and verifies copied FLAC sizes.
6. Copies changed canonical inventory JSON files.
7. Stages only selected batch directories and inventory files, commits if changed, pushes, and verifies the remote commit.

Existing published batch directories are skipped rather than replaced or deleted.

## Verified state

The initial publication completed successfully. Local and GitHub `main` both reached commit `2ffa86277acd00370612c494d2a4f69a5b5b084a`, including two additional batches with 36 FLAC recordings and updated inventory metadata.

## Known limitations

- The runner currently invokes synchronization synchronously with `check=True`. A slow or failed push can delay completion or report an error after audio archival succeeded.
- A failed push that leaves a local commit ahead of `origin/main` is not automatically retried: the current script rejects unequal local and remote heads.
- Concurrent synchronization is not coordinated.
- Automatic creation or updating of canonical narrative metadata for future batches has not been verified.
- A complete new-batch, automatic-publish end-to-end test remains outstanding.

The Audio Evaluation Player is a separate system. Its MP3 copies, `inventory.json`, and website publication are managed by `audio_evaluation_sync.py` in the ACE-Step project, not by this repository's Git synchronization.
