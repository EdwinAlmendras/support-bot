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
- **Per-Chat Settings**: Settings (welcome, cleaner) are now isolated per group.
- **Welcome System**:
  - Implemented **Queue System**: Users are welcomed sequentially to prevent overlap.
  - **Auto-Delete**: Welcome messages self-destruct after 5 seconds.
  - **Image Upload**: Admins can now upload photos directly for the welcome image.
  - **Preview**: Editing a welcome setting now shows a live preview.
- **Security**:
  - Added strict authorization checks to all Admin UI buttons.
- **UX**:
  - Added "Close / Cerrar" button to Admin Dashboard.
  - Automatic cleanup of menu messages.
- Refactored project structure to `src/` layout.
- Updated `cleaner` handlers to respect Admin settings.
- **Link Broadcaster**:
    - Implemented `BroadcastQueue` and `BroadcastService` for scheduled link sharing.
    - Added commands to manage the queue, interval, and status.
- **Remote Management**:
    - Groups can now be added/removed dynamically via `/addgroup` and `/delgroup`.
    - Dashboard now works via DM with group selection support.
- **Smart Link Deletion**:
    - Cleaner now supports messages with multiple links; deletes only if all links are duplicates.
- **Silent Admin Mode**:
    - Administrative actions now auto-delete input messages and previews to keep chats clean.
- **Help Command**:
    - Added `/help` for admins to list all available management commands.
