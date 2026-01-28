# Project TODO

## 🚀 Features to Implement
- [ ] **Rate Limiting**: Prevent users from flooding the chat with messages (Redis/Memory).
- [ ] **Admin Dashboard**: Telegram UI command (`/admin`) to toggle features ON/OFF dynamically.
- [ ] **User Whitelist**: Allow specific users to bypass checks without full Admin privileges.

## 🛠 Engineering & Infrastructure
- [ ] **CI/CD Pipeline**: GitHub Actions for `pytest` and linting (`flake8`/`black`) on push.
- [ ] **Pre-commit Hooks**: Enforce formatting before commit.
- [ ] **Type Checking**: Strict `mypy` integration.

## 🚢 Deployment
- [ ] **Production Config**: `gunicorn` or `uvicorn` production settings (workers, etc.).
- [ ] **Health Checks**: `/health` endpoint for monitoring services.
