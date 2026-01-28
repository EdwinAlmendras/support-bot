# Supabase Setup Guide

## The Confusion: Connection String vs API Keys

Supabase provides two ways to connect:

1.  **API Keys (`sbp_...`)**:
    - Used by the **JavaScript Client** (frontend) or the `supabase-py` client.
    - Connects via HTTP (REST API).
    - Enforces Row Level Security (RLS).

2.  **Connection String (`postgres://...`)**:
    - Used by **Backend code** (Python/SQLAlchemy, Node.js/TypeORM).
    - Connects directly to the PostgreSQL database on port 5432 (or 6543).
    - **This is what `sqlalchemy` needs.**

## How to get the Connection String

1.  Go to your Supabase Project Dashboard.
2.  Click **Project Settings** (cog icon) -> **Database**.
3.  Scroll down to **Connection parameters**.
4.  Switch the tab to **URI**.
5.  It will look like this:
    ```
    postgresql://postgres.yourprojectref:password@aws-0-eu-central-1.pooler.supabase.com:6543/postgres
    ```
6.  **Replace `[YOUR-PASSWORD]`** with the password you set when creating the project.

## Why Direct Connection?

For a Telegram bot, we are running on the server side. A direct SQL connection is:
- Faster (persistent connection).
- Compatible with SQLAlchemy (our ORM).
- Gives full access (bypass RLS for admin tasks).
