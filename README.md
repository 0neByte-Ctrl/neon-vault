# District203 update — read START-HERE.md first

This is the revised portal plus an automatic GitHub importer. The full native District203 import runs on your GitHub deployment, not inside this downloaded source ZIP. Default compatible launches use the separate District203 host unless you configure your own game origin. See START-HERE.md for exact status, preservation rules, limits and update steps.

---

## Original release guide (historical baseline)

# Neon Vault — deployable static release

A combined GameVault / 4texas4 portal themed around the supplied neon-city GIF. The browser tab says **Untitled document - Google Docs**, using the Google Docs favicon supplied in GameVault. This is an independent site, not Google Docs or a Google-affiliated service. Its header and account dialog identify Neon Vault.

## What is included

- 2,162 merged game entries, including a new fully integrated Neon 2048 game.
- 580 entries route to included game files. Included HTML can still depend on online assets. The other entries retain external source/vault links; those vault directories were NOT in the archives.
- 14,226 distinct movie/TV catalog entries with available poster assets. Most entries are metadata only. The ZIPs contain no complete MP4 movie library or portable streaming backend.
- The original bell tracker code unchanged: Regular, SOAR, late start, half day, finals, weekly rotation, holiday exceptions, Central time, local class names.
- 37 cloud shortcuts, the supplied CloudMoon portal, 4texas4 tools, and legacy GameVault Music / Math links.
- Search, categories, source filters, pagination, favorites, recents, movie bookmarks, fullscreen, responsive navigation, reduced-motion support.
- Firebase email/password account integration, reset emails, verification emails, private account libraries and three save-file slots.
- An opt-in, public **Neon 2048** leaderboard, with nicknames rather than email addresses. Client-submitted scores are clearly labeled **not server-verified**.
- DuckDuckGo HTML search form: sends `q` to https://html.duckduckgo.com/html/ in a new tab. It is NOT an embedded search engine or a proxy.

## Deploy on GitHub Pages

1. Extract the ZIP. Upload the **contents of neon-vault/** to a new repository's `main` branch; `index.html` must be at the repository root, not one folder deeper. Include `.nojekyll` and `.github/workflows/pages.yml` (hidden folders may need manual selection).
2. Set `sourceRepository` in `config.js` to your public repository URL. Keep LICENSE, NOTICE, SOURCE-NOTICE.md and source-archives/ available to comply with the original source license, subject to third-party rights below.
3. In repository Settings → Pages, choose **GitHub Actions** as the deployment source.
4. Push your files or run the included Deploy Neon Vault workflow. Your URL is `https://YOUR-USERNAME.github.io/REPOSITORY/`. A `YOUR-USERNAME.github.io` repository also works at the root URL.
5. No build command, Node dependency install, web server or API server is needed. Routing uses URL hashes and application URLs are relative, so project Pages paths work.

For a local preview: `python3 -m http.server 8000` from neon-vault/, then visit http://localhost:8000. Opening index.html directly previews most guest features, but Firebase and embedded engines should be tested over HTTP(S).

## Activate Firebase accounts and cloud saves

Accounts are implemented but **not live** until you configure your own project. No existing GameVault account database is used.

1. Create a project in Firebase Console. Register a Web app.
2. Authentication → Sign-in method → enable **Email/Password**. In Settings → Authorized domains add `YOUR-USERNAME.github.io` and your custom domain if any. For local testing, explicitly add `localhost` if it is not already listed.
3. Create a **Cloud Firestore** database. Choose production mode; do not leave test-mode/open rules in production.
4. Copy the Web app's public Firebase configuration into `config.js` → `firebase`. The Web API key is intended to be public. **Never put service-account JSON, private keys, admin credentials or an email password in the repository.**
5. Paste `firestore.rules` into Firestore → Rules and publish. Under Indexes add a Collection-scope composite index for `leaderboard`: `gameId` Ascending, `score` Descending. Alternatively, with Firebase CLI configured locally: `firebase use YOUR_PROJECT_ID` then `firebase deploy --only firestore:rules,firestore:indexes`.
6. Re-deploy the site. Create an account using a password specifically for this site. Verification emails are needed before publishing leaderboard scores. Reset-password and verification messages come from Firebase.
7. Test with **two separate accounts**: each account must see only its own library and save files. Leaderboard nicknames/scores are publicly readable. Rules deny all other collections by default.
8. Review Firebase quotas, billing settings, password policies and authorized-domain settings. If you open registration to the public, add App Check / abuse controls and moderation before promoting the site. This release does not provide a competitive anti-cheat server or nickname moderation.

## Saving: exactly what works

- **Guest:** favorites, recents, bookmarks and Neon 2048 progress save in this browser's localStorage. Logging off the computer does not erase them; clearing browser data, private browsing and storage restrictions can.
- **Account:** the library syncs to a private Firestore document shortly after a change (1.5-second debounce). Use Sync library before leaving. Immediate browser closing can precede the last network write; the local backup remains.
- **Account switching:** guest and individual account libraries use separate local keys. Signing in does not silently upload guest data. Export the guest library, sign in, and import it explicitly if you want to transfer it.
- **Neon 2048:** board and score save automatically. Arrow keys, WASD, touch swipes and direction buttons are supported. The published best score is separate from the current game. A new game replaces the current checkpoint only after confirmation.
- **Other games:** third-party localStorage, IndexedDB, server accounts and CloudMoon sessions cannot be universally read or synced. Use the game's export/save feature, then upload its save file into one of the three slots. Download and restore through that game's import feature later. Maximum 500 KB per slot. This is a file backup, not automatic emulator/Unity state capture.
- **Movies:** supplied Google Drive previews support manual minute bookmarks and episode notes. Drive embeds do not expose playback time to this portal. When you add an authorized direct media URL, the HTML5 video player automatically saves and resumes its playback position. Streaming failures do not erase bookmarks.
- **Multiple devices:** cloud library updates are last-write-wins, not a conflict-merged database. Avoid editing the same account simultaneously on two devices. Saves cannot be written after an offline computer shuts down.
- Class-name labels in the bell tracker remain local to the browser.
- Export library downloads a JSON backup of the library and 2048 checkpoint, NOT uploaded save files. Download save slots separately.

## Movies, external hosts and CloudMoon

The movie catalog has 113 supplied Google Drive playback tokens (these are resource IDs, not account passwords). Access remains controlled by each file owner's sharing settings. The other remote catalog entries relied on the original project's server/function; that is not a GitHub Pages feature. This release preserves those entries as explicitly catalog-only rather than connecting your project to someone else's service.

For authorized direct video playback, edit `config.js`:

```js
mediaSources: {
  "YOUR-CATALOG-MOVIE-ID": "https://YOUR-MEDIA-HOST.example/your-authorized-video.mp4"
}
```

Use the exact id from data/catalog.js. Sources must be HTTPS, browser-playable and authorized for your audience. Review bandwidth limits before adding large movies to GitHub repositories. GitHub's regular upload and repository limits apply.

CloudMoon remains an external service. Its own accounts, subscriptions, queues and saves are separate from Firebase. The supplied portal contains obfuscated upstream code; it is isolated rather than modified or executed in the parent page. If it cannot load in the isolated frame, Open original launches the original site. No filtering bypass or proxy server is deployed here.

External websites may block iframes, change URLs or go offline. Open original is provided for these cases. This release is a deployable static portal, NOT a guarantee that thousands of third-party links currently work or that the whole catalog can run offline.

## Game isolation / separate game host

Uploaded game and tool code does **not** receive same-origin access to the app by default. The sandbox blocks top navigation and popups and isolates its storage from your Firebase session. Some engines use fetch/IndexedDB/workers and need a real origin, so they may not work in this conservative sandbox. Do not simply add `allow-same-origin` to local untrusted frames: that could expose the app and authentication storage to legacy scripts.

For best compatibility, deploy `iframe/`, `games/`, `texas/` and `js/cdnmap.js` at a **different origin** (another hostname, not another repository path on the same github.io hostname). Set `gameOrigin` in config.js to that origin or the base URL of that separate deployment. The player then gives those cross-origin game frames normal storage while keeping them separate from the account app. Legacy game saving is still owned by the game's origin, not automatically cloud-synced.

PolyTrack's active local entry point loads its supplied engine, not the original Supabase account/rooms/leaderboard extensions. Those originals remain in the source archive. The new leaderboard is only for Neon 2048; other games need individual score adapters and trusted server validation before they can participate.

## Bell schedule maintenance

The source js/schedule.js is preserved unchanged. It includes annual month/day exceptions rather than a live calendar feed. Verify the exceptions against the school's current calendar every year. The time tracker uses America/Chicago regardless of the device's timezone.

## Files

- index.html / style.css / app.js — new responsive portal and integrated 2048.
- config.js — public Firebase config, optional separate game origin, authorized media sources, source-repository URL.
- data/catalog.js — merged searchable catalog.
- js/schedule.js — original bell tracker.
- iframe/, games/polytrack/, texas/ — supplied game/tool files.
- thumbs/, assets/ — original artwork and theme image.
- firestore.rules / firestore.indexes.json / firebase.json — private storage and public score configuration.
- .github/workflows/pages.yml — Pages deployment.
- source-archives/ — original uploaded ZIPs, for provenance and source availability.
- LICENSE / NOTICE / SOURCE-NOTICE.md — original notices and modification statement.

## Verification and known limits

The delivered release was locally tested for navigation, search, filtering, pagination, favorites, guest-library persistence, 2048 moves/saves, file export and mobile layout. See QA-REPORT.md. Firebase live login, emails, cloud sync/rules and third-party network content require your configured project/internet and were not live-tested. There is no fake login, simulated leaderboard or fabricated score data.

Only publish media, game assets and modified source you have the rights to distribute. Retaining an entry or a ZIP is not proof of permission. Remove content if you lack the relevant rights. The source project's AGPL license does not automatically license independent third-party games, movies, trademarks or artwork.
