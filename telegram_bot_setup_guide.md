# Telegram Bot Setup Guide

## Goal

Create a Telegram bot with BotFather, connect it to `main.py`, and understand the full operating workflow for this project.

---

## 1. Create the Telegram bot with BotFather

1. Open Telegram.
2. Search for `BotFather`.
3. Open the verified BotFather chat.
4. Send:

```text
/newbot
```

5. Enter a display name for the bot.

Example:

```text
Wild Lagos Poll Bot
```

6. Enter a unique username ending in `bot`.

Example:

```text
wildlagospollbot
```

7. BotFather will return a bot token.

It will look something like:

```text
1234567890:AAExampleTokenValue
```

Save this token. This becomes `TELEGRAM_BOT_TOKEN`.

---

## 2. Optional BotFather settings

These are not required, but usually useful.

### Set the bot description

Send:

```text
/setdescription
```

Example description:

```text
Vote on Wild Lagos PPV scenes.
```

### Set the bot about text

Send:

```text
/setabouttext
```

Example:

```text
Wild Lagos PPV voting bot
```

### Set the bot profile photo

Send:

```text
/setuserpic
```

### Set commands shown in Telegram

Send:

```text
/setcommands
```

Use:

```text
start - Start the scene voting flow
results - View admin vote totals
```

Important:

- Regular users may see `/results` in the command list.
- The code still protects it with admin-only checks.

---

## 3. Get your Telegram admin user ID

`main.py` restricts `/results` to users listed in `ADMIN_USER_IDS`.

You need your numeric Telegram user ID.

Common ways to get it:

1. Use a Telegram user ID bot such as `userinfobot`.
2. Send any message to that bot.
3. Copy your numeric Telegram ID.

Example:

```text
123456789
```

Later, set:

```text
ADMIN_USER_IDS=123456789
```

If multiple admins need access:

```text
ADMIN_USER_IDS=123456789,987654321
```

---

## 4. Understand how `main.py` works

This project uses normal Telegram polling.

The main workflow in `main.py` is:

### `/start`

- Sends the intro message
- Sends one scene message per configured option
- Adds a vote button to each scene
- Sends video if a `file_id` exists
- Falls back to text if `file_id` is blank

### Vote callback

- Triggered when a user taps a vote button
- Checks whether the poll is closed
- Checks whether the user already voted for that scene
- Writes the vote into SQLite

### `/results`

- Admin-only
- Reads current totals from SQLite
- Sorts results by vote count
- Sends totals back to the admin privately in chat

### Video upload handler

- If an admin sends a video to the bot
- the bot replies with the Telegram `file_id`
- you can later place that `file_id` into the scene configuration

---

## 5. Understand the scene configuration

`main.py` currently defines the 20 scenes in code.

Each scene looks like:

```python
{
    "option_key": "option1",
    "title": "Scene 1",
    "file_id": "",
    "cost": 5.60,
    "callback_data": "vote_option1",
}
```

What each field means:

- `option_key`: internal scene key
- `title`: text shown to users
- `file_id`: Telegram video ID, blank until you collect it
- `cost`: displayed scene cost
- `callback_data`: button value used when the vote is submitted

Rules:

- each `option_key` must be unique
- each `callback_data` must be unique
- users can vote on multiple different scenes
- users cannot vote twice on the same scene

---

## 6. Run the bot locally first

Before deploying, test locally.

Install dependencies:

```bash
pip install -r requirements.txt
```

Set environment variables:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export ADMIN_USER_IDS="123456789"
python3 main.py
```

What should happen:

1. The bot starts.
2. SQLite database tables are created automatically.
3. You can message the bot in Telegram.

---

## 7. Start the poll flow in Telegram

Once the bot is running:

1. Open your bot chat.
2. Send:

```text
/start
```

Expected result:

1. You receive the intro message.
2. You receive 20 scene posts.
3. Each scene post contains a vote button.

If `file_id` is blank for a scene:

- that scene is sent as text

If `file_id` is populated:

- that scene is sent as a Telegram video

---

## 8. Collect Telegram `file_id` values for videos

If you want the bot to send actual videos for scenes, you need Telegram `file_id` values.

Workflow:

1. Start the bot.
2. From an admin account, send one scene video directly to the bot.
3. The bot replies with the Telegram `file_id`.
4. Copy that `file_id`.
5. Open `main.py`.
6. Find the matching scene entry in `VIDEO_DATA`.
7. Paste the `file_id` into that scene.
8. Repeat for all scenes.
9. Redeploy or restart the bot.

After this, `/start` will send the saved videos instead of text for those scenes.

---

## 9. Understand the voting workflow

Here is the full user flow:

1. User opens the bot.
2. User sends `/start`.
3. Bot sends scene posts with vote buttons.
4. User taps a vote button.
5. Bot checks whether voting is still open.
6. Bot checks whether that same user already voted for that same scene.
7. If not, the vote is stored in SQLite.
8. User can continue voting on other scenes.
9. User cannot vote twice on the same scene.

This matches your requirement:

- multi-scene voting
- duplicate prevention per scene
- persistent storage

---

## 10. Understand the admin workflow

Your workflow as admin is:

1. Start the bot locally or on Railway.
2. Send `/start` to test the user flow.
3. Send sample votes from test accounts if needed.
4. Run:

```text
/results
```

5. Review the live vote totals.
6. If needed, redeploy without losing votes as long as SQLite is on the persistent volume.

Important:

- Users do not need live tally visibility.
- Only admins should use `/results`.

---

## 11. Update poll close date if needed

The close time is defined directly in `main.py`.

Look for:

```python
POLL_CLOSE = datetime(2026, 5, 9, 22, 0, tzinfo=NEW_YORK)
```

To change the close date:

1. Edit the date and time.
2. Save the file.
3. Restart locally or redeploy on Railway.

The bot will reject new votes after that timestamp.

---

## 12. Recommended real workflow for this project

Use this order:

1. Create the bot in BotFather.
2. Save the bot token.
3. Get your Telegram numeric user ID.
4. Run the bot locally.
5. Test `/start`, voting, and `/results`.
6. Send videos to the bot and collect `file_id` values.
7. Add those `file_id` values to `main.py`.
8. Test again locally.
9. Deploy to Railway with a persistent volume.
10. Test again after deployment.

---

## 13. Common mistakes

### Bot token is wrong

Symptom:

- bot fails to start

Fix:

- regenerate or re-copy the BotFather token

### `/results` does not work for you

Symptom:

- bot says restricted

Fix:

- add your numeric Telegram user ID to `ADMIN_USER_IDS`

### Votes disappear

Symptom:

- results reset after restart or redeploy

Fix:

- use SQLite on Railway volume storage

### Videos are not showing in `/start`

Symptom:

- scene cards show text only

Fix:

- collect and add correct `file_id` values

---

## 14. Required environment variables summary

Local:

```bash
export TELEGRAM_BOT_TOKEN="your_bot_token"
export ADMIN_USER_IDS="123456789"
python3 main.py
```

Railway:

```text
TELEGRAM_BOT_TOKEN=your_bot_token
ADMIN_USER_IDS=123456789
BOT_DB_PATH=/app/data/bot_data.sqlite3
```

---

## 15. Final checklist

- Bot created in BotFather
- Token saved
- Admin user ID collected
- `main.py` tested locally
- Scene titles configured
- Optional `file_id` values collected
- Railway volume attached
- Railway variables configured
- `/start` tested
- vote flow tested
- `/results` tested
