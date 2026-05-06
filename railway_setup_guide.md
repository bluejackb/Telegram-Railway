# Railway Setup Guide

## Goal

Deploy the Wild Lagos Telegram poll bot on Railway with persistent SQLite storage.

This guide assumes you already have:

- `main.py`
- `requirements.txt`
- a Telegram bot token
- your Telegram numeric user ID for admin access

---

## 1. Prepare the project folder

Your folder should contain at least:

```text
main.py
requirements.txt
```

Optional supporting files:

```text
updated telegram_bot_handoff.md
telegram_bot_setup_guide.md
railway_setup_guide.md
```

---

## 2. Create a Railway account

1. Go to [Railway](https://railway.com/).
2. Sign up or log in.
3. Connect your GitHub account if Railway asks.
4. Upgrade to the `Hobby` plan if you want this bot to run continuously.

Notes:

- Railway Free is fine for brief testing only.
- For a real always-on bot, use `Hobby`.

---

## 3. Put the bot code in GitHub

Railway is simplest when deploying from GitHub.

1. Create a new GitHub repository.
2. Upload `main.py` and `requirements.txt`.
3. Commit and push the files.

If you prefer, you can also deploy with the Railway CLI, but GitHub deploys are simpler for this bot.

---

## 4. Create a new Railway project

1. In Railway, click `New Project`.
2. Choose `Deploy from GitHub repo`.
3. Select the repository containing this bot.
4. Wait for Railway to create the service.

Railway should detect this as a Python app from `requirements.txt`.

---

## 5. Attach a persistent volume

This step matters because the bot stores votes in SQLite.

1. Open your Railway service.
2. Add a `Volume`.
3. Attach it to the bot service.
4. Set the mount path to:

```text
/app/data
```

Why:

- Railway containers use ephemeral storage by default.
- Without a volume, redeploys or restarts can wipe your SQLite database.

---

## 6. Set environment variables

Open the Railway service variables/settings and add:

### Required

```text
TELEGRAM_BOT_TOKEN=your_real_bot_token
ADMIN_USER_IDS=123456789
BOT_DB_PATH=/app/data/bot_data.sqlite3
```

What each variable does:

- `TELEGRAM_BOT_TOKEN`: token from BotFather
- `ADMIN_USER_IDS`: comma-separated Telegram user IDs allowed to use `/results`
- `BOT_DB_PATH`: forces SQLite to use the mounted persistent volume

If you have multiple admins:

```text
ADMIN_USER_IDS=123456789,987654321
```

---

## 7. Confirm the start command

Railway may auto-detect the app, but if needed set the start command manually:

```text
python3 main.py
```

You usually do this in the service settings under start command or deploy settings.

---

## 8. Set restart policy

For a bot, this should be:

```text
Always
```

Why:

- If the process crashes, Railway will restart it automatically.
- Bots should behave like always-on workers.

---

## 9. Deploy the service

1. Trigger the initial deployment.
2. Wait for the build and start steps to finish.
3. Open the logs.
4. Confirm the bot starts without errors.

Healthy startup should show your bot process running and no token/database errors.

---

## 10. Test the deployment

After Railway says the service is running:

1. Open Telegram.
2. Find your bot.
3. Send `/start`.
4. Confirm the bot sends the intro plus all 20 scene messages.
5. Tap vote buttons on a few scenes.
6. Confirm repeat voting on the same scene is blocked.
7. Confirm voting on a different scene still works.
8. Send `/results` from your admin account.
9. Confirm totals are shown.

---

## 11. Verify persistence

You specifically need to confirm SQLite persistence.

1. Cast a few votes.
2. Trigger a redeploy or restart in Railway.
3. Wait for the service to come back up.
4. Run `/results` again.
5. Confirm the same votes are still present.

If votes disappear, your database is not on the mounted volume.

---

## 12. Update scene video `file_id` values later

When you are ready to replace text-only scene posts with real videos:

1. Send a video to the bot from an admin account.
2. The bot replies with the Telegram `file_id`.
3. Copy that `file_id`.
4. Insert it into the matching scene entry in `VIDEO_DATA` inside `main.py`.
5. Redeploy the bot.

Note:

- The current code returns `file_id` to admins.
- The current code does not include an in-app admin command to write `file_id` values into SQLite automatically.

---

## 13. Ongoing workflow

Your ongoing deployment workflow is:

1. Edit `main.py` locally.
2. Commit changes to GitHub.
3. Push to GitHub.
4. Railway auto-redeploys.
5. Check logs after deploy.
6. Run `/results` or `/start` to verify behavior.

---

## Common mistakes

### Bot starts but votes disappear later

Cause:

- `BOT_DB_PATH` is not pointing at the mounted volume
- or the volume was never attached

Fix:

- mount volume at `/app/data`
- set `BOT_DB_PATH=/app/data/bot_data.sqlite3`

### `/results` says restricted

Cause:

- your Telegram user ID is not listed in `ADMIN_USER_IDS`

Fix:

- add your numeric Telegram user ID
- redeploy or restart

### Bot does not start

Cause:

- invalid or missing `TELEGRAM_BOT_TOKEN`

Fix:

- re-copy the token from BotFather

### Only text messages appear, no videos

Cause:

- `file_id` values are still blank

Fix:

- collect Telegram `file_id` values and add them to the scene configuration

---

## Recommended final Railway configuration

Use this exact baseline:

```text
Plan: Hobby
Volume mount path: /app/data
Start command: python3 main.py
Restart policy: Always
TELEGRAM_BOT_TOKEN=...
ADMIN_USER_IDS=123456789
BOT_DB_PATH=/app/data/bot_data.sqlite3
```
