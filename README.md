# Telegram Bot Support System

A scalable Telegram bot with administration features, link deduplication, and Postgres/SQLite support.

## Features

- **Link Deduplication**: prevents users from spamming the same link multiple times in a chat.
- **Service Message Cleanup**: Automatically deletes "User Joined" and "User Left" messages.
- **Admin Bypass**: Administrators (defined in config) can bypass restrictions.
- **Dockerized**: Easy deployment with Docker and Docker Compose.
- **Scalable**: Built with `aiogram`, `SQLAlchemy`, and a modular architecture.

## Getting Started

### Prerequisites

- Python 3.11+
- [Docker](https://www.docker.com/) (Optional)

### Installation

1.  Clone the repository.
2.  Install dependencies:
    ```bash
    pip install -r requirements.txt
    ```
3.  Copy `.env.example` to `.env` and configure:
    ```ini
    BOT_TOKEN=your_bot_token
    ADMIN_IDS=12345,67890
    DATABASE_URL=sqlite+aiosqlite:///data/bot.db
    ```

### Running

**Production:**
```bash
python main.py
```

**Development (Auto-reload):**
```bash
python dev.py
# or
docker-compose -f docker-compose.dev.yml up --build
```

### Testing

Run the test suite:
```bash
pytest
```

## Database

Supports both **SQLite** (default) and **PostgreSQL** (Supabase).
To use Supabase, set `DATABASE_URL` in `.env`:
```ini
DATABASE_URL=postgresql+asyncpg://user:pass@host:port/postgres
```
See `docs/supabase_setup.md` for more details.
# support-bot
