# District203 revision verification

Passed locally: importer unit tests; syntax checks; stable existing IDs; exact/alias matching; no fuzzy sequel matches; unmatched game records unchanged; unrelated collections unchanged; byte-for-byte preservation of 1,908 original game, configuration and bell-schedule files; desktop/mobile portal navigation and overflow checks; GIF play/pause controls; first-party 2048; Continue-last-game.

Visually reviewed: new desktop home and mobile Settings. Source GIF verified as 36 frames, 60 ms/frame, infinite loop.

NOT completed here: full District203 source download; production-sized import; actual native District203 game launches; live Firebase; GitHub Pages deployment; third-party website availability. A blocked sandbox download and unavailable general network prevented those checks. The included GitHub workflow performs the full import and the native checks described in START-HERE.md before deploying.

Reports from a completed GitHub build are available in data/district-import.json and data/native-launch-tests.json and as a workflow artifact. A pending/live-links state in the seed package is not a completed native import.
