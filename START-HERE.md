# Neon Vault — District203 update

## You do not need to split the large ZIP

This update uses the public repository https://github.com/district203/district203.github.io directly. GitHub's build runner downloads the upstream files, merges the catalog and deploys the resulting static website.

**Important status:** this download is the updated portal and importer, not a locally completed download of District203's large game library. The complete native import and representative native game tests run when you deploy on GitHub. They have NOT run against the full upstream library in this chat environment.

## Easiest update: use the small Update-Only ZIP

1. Back up your current Neon Vault repository.
2. Extract the Update-Only ZIP and copy its contents into your existing repository root, replacing the listed files. Do not put the update inside an extra folder. Include the hidden `.github` folder.
3. **Keep your existing config.js**, Firebase project configuration, game files and saved deployment settings. The small ZIP does not include or overwrite them.
4. In GitHub → repository Settings → Pages, choose **GitHub Actions**.
5. Push to the `main` branch. The included workflow runs automatically. Or open Actions → **Import District203 and deploy Neon Vault** → Run workflow.
6. Wait for the workflow to finish successfully. Large libraries can take a while. Do not close a running GitHub workflow; it runs on GitHub, not your computer.
7. Open the existing Pages URL. Home / Settings show the completed import counts. Under Actions, download `district203-import-and-tests` for the matching and launch reports.

The full ZIP is an alternative starting point if you do not already have the previous release. Its `neon-vault/` contents go at your repository root. Copy over your existing Firebase config before deploying. Use GitHub Desktop or git for large file uploads; the GitHub website has per-file upload limits.

## Matching and preservation rules

- Existing game IDs stay stable, preserving Neon Vault favorite/history references.
- Exact normalized names and paths match differences in spaces, punctuation and a small explicit alias table. There is no fuzzy sequel matching.
- Matching games switch to District203's version. New District203 games are appended.
- Games with no unambiguous match stay unchanged. Missing upstream game entry points do not overwrite an old game.
- The distinct first-party **Neon 2048** is preserved, including its supported Firebase progress and leaderboard. The original third-party **2048** can be replaced independently.
- Existing movies, cloud shortcuts, save files, account integration and bell-schedule code stay intact.
- The importer records every replacement, addition, missing entry and size-limited native folder in `data/district-import.json`. It also keeps the replaced original catalog entries in `data/district-replaced-originals.json` for reference.

## Native files versus compatible game launches

The previous release isolated games without same-origin storage permissions. That can stop engines that need localStorage, IndexedDB or workers. Giving unaudited, same-origin game scripts those permissions could also expose your portal/account storage.

This update enables normal browser capabilities for games on a **different origin**, while keeping your Firebase account isolated:

- Default **Compatible** mode launches District203's hosted version in the player. It requires that external website to be available; it is not an offline/native claim.
- The GitHub build also copies complete native game folders into `district203/`, up to an **800 MB total deployed-site budget** to stay below GitHub Pages' site-size limit. It never deliberately copies half of a game folder to meet that budget. Catalog entries beyond the budget remain available through the District203 host.
- If you host the copied game files on a separate hostname and set `gameOrigin` in config.js, Compatible mode uses those native copies instead. Another repository path on the same hostname is NOT a different origin. Keep the `district203/` path when uploading the game payload.
- Settings → **Included native files** is an optional restricted sandbox mode on the main site. It is useful for compatible engines, but storage/worker-dependent games may still fail. It does not grant unsafe access to your account session.
- Static root asset references that point to copied source files are rewritten for subfolder hosting. Some dynamically constructed URLs and shared assets can still need game-specific work; use the launch report instead of assuming every engine was validated.

The workflow requires a working native 2048 launch and keyboard movement before publishing. It also attempts surface checks for Hextris and Chrome Dino if copied; other titles are not individually verified. If the mandatory test fails, deployment stops and the previous deployed site remains in place.

## New visible controls

- The supplied **36-frame looping GIF** is a real image layer on the homepage, animated by default.
- Play/Pause animation control; Settings can also follow the system's reduced-motion preference.
- Home Quick Play: Continue last game, random game, recent-game shortcuts.
- Sort by original order, District203 first, popularity or A–Z.
- District203 source filter, native-copy labels and import-status details.
- Settings: browser-tab title, optional quick-exit shortcut, optional close-tab reminder and recent-history clearing.

The default browser title remains **Untitled document - Google Docs** and the original supplied favicon remains. The actual site and sign-in dialog identify Neon Vault, not Google.

Favorites, categories, random play, schedule, account libraries, manual movie bookmarks and save-file backups already existed and are retained, not presented as new District203 inventions. Upstream ads, sponsor promotions, owner/contact details, unsupported proxy/server features and third-party account systems were not transplanted into your site.

## Build requirements and limitations

- GitHub Actions must be enabled in your repository, with Pages configured for Actions.
- The build needs internet access to GitHub's API and raw-file host. No GitHub personal access token or Firebase admin key is embedded.
- It records the exact upstream commit and does not execute upstream package scripts or workflows.
- If GitHub returns a truncated file tree or a download fails, the build stops rather than pretending the import completed. Re-run after a transient error.
- If you need to pin the upstream version, use Run workflow → `district_ref` with the desired commit.
- To import an extracted source locally: `python scripts/merge_district.py --site PATH_TO_UNMERGED_SITE --source PATH_TO_DISTRICT203 --budget-mb 800`.
- Live Firebase login, emails, sync and leaderboard still require your existing configured Firebase project. No Firebase credentials were changed in this update.
- GitHub Pages remains a static host: it cannot supply a movie-streaming server or universal game-state sync.

## Verification performed here

Passed: importer unit tests, no fuzzy sequel replacement, unsafe-path rejection, stable IDs, unmatched-game preservation, unrelated movies/cloud/tools preservation, byte checks on original payload/config/schedule files, browser navigation and overflow at desktop/mobile widths, animation controls, integrated Neon 2048 and the Continue shortcut.

Visually inspected: updated desktop homepage and mobile Settings. Verified that the source GIF has 36 frames and loops indefinitely.

Not performed here: the full District203 download/import, live native District203 game launches, GitHub deployment, Firebase live services or third-party service availability. Those are explicitly deferred to the included workflow and your deployed environment.

Original license notices remain. Review your rights to redistribute third-party games/media. An upstream repository license is not blanket permission for every bundled asset.
