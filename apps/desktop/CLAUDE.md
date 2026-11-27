# apps/desktop/CLAUDE.md

Rules for the desktop app. These add to the root `CLAUDE.md`.

- Frontend: React + TS in `src/`. Rust side in `src-tauri/`.
- Tauri commands are thin: validate input, call `engine` / app logic, return typed results.
  No simulation logic in the Tauri layer or the frontend.
- Shared components belong in `packages/ui`, not here.
- Keep Tauri permissions in `src-tauri/capabilities/` minimal; adding a permission is a 🟠
  review item and must be explained in the PR.
- Bundling (icons, installers, signing, updater) is set up in Phase 5 — `bundle.active` is
  false until then.
