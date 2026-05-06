# Telegram Bot Refactor Handoff with Full `main.py`

## Goal

Create a standalone Telegram poll bot for a **20-option Wild Lagos 🇳🇬 PPV poll**.

---

## Core Behavior

The bot must:

- Run continuously until poll close
- Accept votes anytime before close
- Prevent duplicate votes
- Maintain a live vote tally
- Support 20 dynamic options
- Display live sorted results
- Run without Replit/Flask hacks

---

## Runtime Model (Important)

This bot uses:

```
await application.run_polling()
```

### What that means

- Telegram pushes updates to your bot
- Users can vote at any time
- Bot handles requests concurrently (async)

### Requirement

The bot must be **hosted and running continuously**.

If the process stops:

- Votes stop
- Memory resets (votes lost)

---

## Vote Tally Behavior

Yes — votes update immediately:

- Each vote increments `votes[optionX]`
- `/results` reflects latest counts
- Selected video caption updates live

---

## ⚠️ Critical Limitation

Votes are stored in memory:

```
votes = {}voted_users = {}
```

### Consequences

- Restart = **all votes lost**
- Crash = **all votes lost**

### Recommendation (strong)

Add persistence:

- SQLite (minimum)
- PostgreSQL (better)
- Redis (fastest)

---

## Poll Configuration

```
poll_close = timezone("US/Eastern").localize(datetime(2026, 5, 9, 22, 0))
```

- May 9, 2026
- 10:00 PM EST

---

## Video Data Schema

20 entries required:

```
{    "title": "Scene 1",    "file_id": "",    "cost": 5.60,    "callback": "vote_option1"}
```

### Notes

- `file_id` initially blank
- `link` removed
- callbacks must map 1–20

---

## Getting Telegram `file_id`

### Steps

1. Run bot
2. Send video to bot
3. Bot replies with `file_id`
4. Copy it into `video_data`
5. Repeat for all 20 videos

---

# Full `main.py`

```
import asyncioimport osimport refrom datetime import datetimefrom pytz import timezonefrom telegram import InlineKeyboardButton, InlineKeyboardMarkup, Updatefrom telegram.ext import (    ApplicationBuilder,    CallbackQueryHandler,    CommandHandler,    ContextTypes,    MessageHandler,    filters,)BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")if not BOT_TOKEN:    raise RuntimeError("Set TELEGRAM_BOT_TOKEN env variable")EASTERN = timezone("US/Eastern")poll_close = EASTERN.localize(datetime(2026, 5, 9, 22, 0))video_data = [    {"title": f"Scene {i}", "file_id": "", "cost": 5.60, "callback": f"vote_option{i}"}    for i in range(1, 21)]votes = {f"option{i}": 0 for i in range(1, 21)}voted_users = {}def escape(text):    return re.sub(r'([_*\[\]()~`>#+\-=|{}.!])', r'\\\1', str(text))def get_key(cb):    return cb.replace("vote_", "")async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):    msg = (        "<b>🔥 Welcome to the ABM Poll Bot!</b>\n\n"        "🎥 <b>Wild Lagos 🇳🇬 PPV Poll</b>\n\n"        "💰 <b>20 PPV scenes — $112 total</b>\n\n"        "🗳️ Vote for the scenes you want.\n\n"        f"⏳ Voting closes: <b>{poll_close.strftime('%B %d, %I:%M %p EST')}</b>\n\n"        "👇 Watch clips below and vote!"    )    await update.message.reply_text(msg, parse_mode="HTML")    for v in video_data:        caption = (            f"🎬 *{escape(v['title'])}*\n\n"            f"💵 Cost: \\${v['cost']}\n\n"            "Vote below\\!"        )        kb = [[InlineKeyboardButton(f"✅ Vote for {v['title']}", callback_data=v["callback"])]]        if v["file_id"]:            await update.message.reply_video(                v["file_id"],                caption=caption,                parse_mode="MarkdownV2",                reply_markup=InlineKeyboardMarkup(kb)            )        else:            await update.message.reply_text(                caption,                parse_mode="MarkdownV2",                reply_markup=InlineKeyboardMarkup(kb)            )async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE):    q = update.callback_query    uid = q.from_user.id    data = q.data    now = datetime.now(EASTERN)    if now > poll_close:        await q.answer("Voting closed", show_alert=True)        return    if uid in voted_users:        await q.answer("Already voted", show_alert=True)        return    key = get_key(data)    voted_users[uid] = key    votes[key] += 1    await q.answer("Vote recorded")async def results(update: Update, context: ContextTypes.DEFAULT_TYPE):    sorted_items = sorted(        enumerate(video_data, 1),        key=lambda x: votes[f"option{x[0]}"],        reverse=True    )    lines = ["📊 *Live Results*\n"]    for i, v in sorted_items:        lines.append(f"{v['title']}: {votes[f'option{i}']}")    await update.message.reply_text(        escape("\n".join(lines)),        parse_mode="MarkdownV2"    )async def debug(update: Update, context: ContextTypes.DEFAULT_TYPE):    if update.message.video:        await update.message.reply_text(update.message.video.file_id)async def main():    app = ApplicationBuilder().token(BOT_TOKEN).build()    app.add_handler(CommandHandler("start", start))    app.add_handler(CommandHandler("results", results))    app.add_handler(CallbackQueryHandler(vote))    app.add_handler(MessageHandler(filters.VIDEO, debug))    await app.run_polling()if __name__ == "__main__":    asyncio.run(main())
```

---

## Project Structure

```
project/  main.py  requirements.txt
```

---

## requirements.txt

```
python-telegram-botpytz
```

---

## Run

```
export TELEGRAM_BOT_TOKEN=your_tokenpython main.py
```

---

## Hosting (Required)

Use:

- Railway
- Render
- VPS
- Docker

Do NOT rely on local machine unless always on.

---

## Acceptance Checklist

- [ ]  20 options display
- [ ]  Voting works once per user
- [ ]  Voting stops after deadline
- [ ]  Results update live
- [ ]  No crashes with empty file_id
- [ ]  Bot runs continuously

---