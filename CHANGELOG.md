# Changelog

All notable changes to this project will be documented in this file.

## [Unreleased]

### Added
- **Authentication**: `AdminFilter` logic.
- **Database**:
  - SQLite default support.
  - PostgreSQL (Supabase) support via `DATABASE_URL`.
  - `SeenLink` model for deduplication.
- **Docker**:
  - `Dockerfile` for production.
  - `docker-compose.yml` for production.
  - `docker-compose.dev.yml` for development (volume mapping).
- **Development**:
  - `dev.py` script for hot-reloading.
  - `watchdog` dependency.
- **Testing**:
  - `pytest` suite for filters and DB logic.
- **Features**:
  - **Welcome Message**:
    - "Smart" welcome that deletes the previous one (Anti-flood).
    - Customizable Text, Image, and Group Link via `/admin`.
    - Concurrency safe (Async locks).
  - **Admin Dashboard**:
    - `/admin` command to toggle features dynamically.
    - `BotSetting` model for persistent configuration.
    - Inline Keyboard UI for settings.
  - Auto-deletion of "User Joined/Left" messages (Toggleable).
  - Link deduplication logic (Toggleable).
- **Project Structure**:
  - Added `TODO.md` roadmap.
  - Added `.gitignore`.

### Changed
- Refactored project structure to `src/` layout.
- Updated `cleaner` handlers to respect Admin settings.
