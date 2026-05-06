# Telegram Bot Refactor Handoff

## Goal

Build a standalone Telegram bot for the **Wild Lagos PPV scene poll**.

This version must be runnable as-is and must persist votes in SQLite so restarts do not lose data.

---

## Product Rules

- The poll contains 20 scene options.
- Users can vote for multiple scenes.
- A user may vote only once per scene.
- Voting remains open until the configured close time.
- Users do not need to see live results.
- Admins must be able to view results privately with a command.
- The bot must run as a normal long-lived Telegram bot using polling.

---

## Runtime Model

The bot runs with:

```python
application.run_polling()
```

This means:

- Telegram pushes updates to the bot while it is running.
- The process must stay online for users to interact with it.
- Votes are persisted in SQLite, so a restart does not erase prior votes.

---

## Storage Model

Use SQLite for persistence.

Required tables:

### `videos`

Stores the 20 configured scenes.

Suggested columns:

- `option_key TEXT PRIMARY KEY`
- `title TEXT NOT NULL`
- `file_id TEXT NOT NULL DEFAULT ''`
- `cost REAL NOT NULL`
- `callback_data TEXT NOT NULL UNIQUE`

### `votes`

Stores one row per user per scene.

Suggested columns:

- `user_id INTEGER NOT NULL`
- `option_key TEXT NOT NULL`
- `voted_at TEXT NOT NULL`

Constraint:

- `UNIQUE(user_id, option_key)`

This uniqueness rule prevents duplicate votes on the same scene while still allowing one user to vote for multiple different scenes.

---

## Poll Close

The poll closes at:

```python
datetime(2026, 5, 9, 22, 0, tzinfo=ZoneInfo("America/New_York"))
```

Display it as local New York time.

Note: May 9, 2026 is daylight saving time in New York, so the displayed abbreviation should be `EDT`, not `EST`.

---

## Video Configuration

The bot should keep the 20 scene definitions in code for now.

Schema per entry:

```python
{
    "option_key": "option1",
    "title": "Scene 1",
    "file_id": "",
    "cost": 5.60,
    "callback_data": "vote_option1",
}
```

Rules:

- Exactly 20 entries are expected.
- `file_id` may be blank initially.
- If `file_id` is blank, send a text message instead of a video.
- `option_key` and `callback_data` must map consistently.

---

## Bot Commands

### `/start`

- Sends the intro message.
- Sends one message per scene with a vote button.
- If a scene has a `file_id`, send it as a video with caption.
- Otherwise send text with the same vote button.

### Vote button callback

- Reject votes after the deadline.
- Reject duplicate votes for the same user and same scene.
- Allow the same user to vote on other scenes.
- Persist the vote immediately in SQLite.

### `/results`

- Shows results sorted by highest vote count.
- This command is for admin use only.
- Restrict access with an `ADMIN_USER_IDS` environment variable containing comma-separated Telegram user IDs.

### Video upload handler

- When an admin sends a video to the bot, reply with the Telegram `file_id`.
- This is used to populate the scene configuration.

---

## Environment Variables

Required:

- `TELEGRAM_BOT_TOKEN`

Optional:

- `ADMIN_USER_IDS`
- `BOT_DB_PATH`

Defaults:

- `BOT_DB_PATH=$RAILWAY_VOLUME_MOUNT_PATH/bot_data.sqlite3` on Railway when a volume is attached
- otherwise `BOT_DB_PATH=/app/data/bot_data.sqlite3`

---

## File Layout

```text
project/
  main.py
  requirements.txt
  bot_data.sqlite3   # created automatically at runtime
```

---

## Requirements

```text
python-telegram-bot>=21,<22
```

SQLite is included with Python, so no separate package is required.

---

## Run Locally

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export ADMIN_USER_IDS="123456789"
python3 main.py
```

---

## Hosting Notes

Use a host that can keep a Python process running continuously, such as:

- Railway
- Render
- VPS
- Docker on any always-on host

### Railway-specific setup

For Railway, attach a persistent volume to the service and mount it at:

```text
/app/data
```

Recommended Railway variables:

- `TELEGRAM_BOT_TOKEN=...`
- `ADMIN_USER_IDS=123456789`
- `BOT_DB_PATH=/app/data/bot_data.sqlite3`

Recommended service settings:

- Plan: `Hobby`
- Restart policy: `Always`
- Start command: `python3 main.py` if Railway does not detect it automatically

Do not rely on Railway ephemeral storage for SQLite. The database file must live on the mounted volume.

---

## Acceptance Checklist

- [ ] 20 scene options are sent by `/start`
- [ ] A user can vote for multiple scenes
- [ ] A user cannot vote twice for the same scene
- [ ] Votes remain after process restart
- [ ] Voting stops after the configured deadline
- [ ] `/results` is admin-only
- [ ] Empty `file_id` values do not crash the bot
- [ ] Video uploads return `file_id` for admin setup
