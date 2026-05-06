import asyncio
import logging
import os
import sqlite3
from datetime import datetime
from pathlib import Path
from zoneinfo import ZoneInfo

from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.constants import ParseMode
from telegram.ext import (
    Application,
    CallbackQueryHandler,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)


logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
LOGGER = logging.getLogger(__name__)

BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
if not BOT_TOKEN:
    raise RuntimeError("Set TELEGRAM_BOT_TOKEN")

NEW_YORK = ZoneInfo("America/New_York")
POLL_CLOSE = datetime(2026, 5, 9, 22, 0, tzinfo=NEW_YORK)
if os.getenv("RAILWAY_ENVIRONMENT") or os.getenv("RAILWAY_VOLUME_MOUNT_PATH"):
    default_db_dir = Path(os.getenv("RAILWAY_VOLUME_MOUNT_PATH", "/app/data"))
else:
    default_db_dir = Path(__file__).resolve().parent
DEFAULT_DB_PATH = default_db_dir / "bot_data.sqlite3"
DB_PATH = Path(os.getenv("BOT_DB_PATH", str(DEFAULT_DB_PATH)))
ADMIN_USER_IDS = {
    int(user_id.strip())
    for user_id in os.getenv("ADMIN_USER_IDS", "").split(",")
    if user_id.strip()
}

VIDEO_DATA = [
    {"option_key": "option1", "title": "The Good Side Of Lagos", "file_id": "BAACAgEAAxkBAAIBYmn7QJlksldLl5oMdlc5GLjLreYJAAMGAAJgxthHvB73FlhDAZA7BA", "cost": 8.00, "callback_data": "vote_option1"},
    {"option_key": "option2", "title": "Elizabeth of Ogbomosho", "file_id": "BAACAgEAAxkBAAIBZGn7Qdu9BNOE4IlTVXalo8-AsVikAAIBBgACYMbYR46CvzKLRbfOOwQ", "cost": 4.00, "callback_data": "vote_option2"},
    {"option_key": "option3", "title": "Badbooty Orisha Devours BBC on Sunny Sunday", "file_id": "BAACAgEAAxkBAAIBZmn7R-BG0nTMNYaijK20xSNW6_4hAAIMBgACYMbYR9rB2NW589SqOwQ", "cost": 3.00, "callback_data": "vote_option3"},
    {"option_key": "option4", "title": "A Day in Lagos- Vol I", "file_id": "BAACAgEAAxkBAAIBaGn7SHqXES3C6ezjrdCKr4rxpXfCAAINBgACYMbYR2PhcVFVOUAJOwQ", "cost": 8.00, "callback_data": "vote_option4"},
    {"option_key": "option5", "title": "The Cream Factory Between Her Thighs", "file_id": "BAACAgEAAxkBAAIBamn7SQs19hC4T7NKDmb_0EteY90NAAIOBgACYMbYRz2ilvY2OuqzOwQ", "cost": 7.00, "callback_data": "vote_option5"},
    {"option_key": "option6", "title": "Exploring Lagos City", "file_id": "BAACAgEAAxkBAAIBbGn7SfzmIzWw9VBKjzP9Qjnde_gJAAIPBgACYMbYRzA9Jgii031ROwQ", "cost": 8.00, "callback_data": "vote_option6"},
    {"option_key": "option7", "title": "Aisha Azzara with a Beautiful Body Fucked Roughly", "file_id": "BAACAgEAAxkBAAIBbmn7SyMjviCzfCn83y1fELbGni9eAAIRBgACYMbYR31ovC6ubvDgOwQ", "cost": 4.00, "callback_data": "vote_option7"},
    {"option_key": "option8", "title": "What Happened in Room 306", "file_id": "BAACAgEAAxkBAAIBcGn7S4EgJKdYjM8nVN08uf7nqnfqAAISBgACYMbYR2rzCCLU9MpgOwQ", "cost": 3.00, "callback_data": "vote_option8"},
    {"option_key": "option9", "title": "Vox-Pop Gone Wrong Ft Asari & Gray", "file_id": "BAACAgEAAxkBAAIBcmn7TCHyFUgEVSn9rVC5dxnxYmaJAAIUBgACYMbYR6q4I2RGvsZUOwQ", "cost": 8.00, "callback_data": "vote_option9"},
    {"option_key": "option10", "title": "The Wild Foursome Ft TopBitch (Part II)", "file_id": "BAACAgEAAxkBAAIBdGn7UnWEjjma0B4NzVzaQE7MXJ3YAAIYBgACYMbYR-dCiqwFX1baOwQ", "cost": 4.00, "callback_data": "vote_option10"},
    {"option_key": "option11", "title": "Beach Night Out Ft. EbonyChoco & TopBitch", "file_id": "BAACAgEAAxkBAAIBdmn7Usc48Z2IJYXx3JMXzpxNcG51AAIZBgACYMbYRw9-D2YXb6nBOwQ", "cost": 8.00, "callback_data": "vote_option11"},
    {"option_key": "option12", "title": "Sensual Fuck with ASARI and KING SLEDGE", "file_id": "BAACAgEAAxkBAAIBeGn7UxQDcXcnTuh1ui97wHSttEqSAAIaBgACYMbYR1mlE3yFQUnSOwQ", "cost": 8.00, "callback_data": "vote_option12"},
    {"option_key": "option13", "title": "Two Girls and A Cock", "file_id": "BAACAgEAAxkBAAIBemn7U1cwe3WM12NQySWGQDGoKG2IAAIbBgACYMbYR6ZWkY7AJY_zOwQ", "cost": 8.00, "callback_data": "vote_option13"},
    {"option_key": "option14", "title": "Aisha with the Body Strikes Again", "file_id": "BAACAgEAAxkBAAIBfGn7U6kQLI8ICRWDoGT6xAdt3IH4AAIcBgACYMbYR3YFC8j627WBOwQ", "cost": 4.00, "callback_data": "vote_option14"},
    {"option_key": "option15", "title": "The Trenches Fuck", "file_id": "BAACAgEAAxkBAAIBfmn7VBL69S2ICwedVt2at9qA2HkjAAIdBgACYMbYR1Ep_HSsBp5qOwQ", "cost": 3.00, "callback_data": "vote_option15"},
    {"option_key": "option16", "title": "Femi and Zara Ft TopBitch (Pilot Movie)", "file_id": "BAACAgEAAxkBAAIBgGn7VLW3Dru5T-FfrhcQyq9YnvpNAAIeBgACYMbYR8jS0A-R3mPBOwQ", "cost": 8.00, "callback_data": "vote_option16"},
    {"option_key": "option17", "title": "Big Dicks VS Content Creators", "file_id": "BAACAgEAAxkBAAIBgmn7VYhuNcZVBQleUz1lfs_hrUSkAAIgBgACYMbYR4jb5fq6FPp4OwQ", "cost": 8.00, "callback_data": "vote_option17"},
    {"option_key": "option18", "title": "Beautiful African Queen Takes Pipping Like a PRO", "file_id": "BAACAgEAAxkBAAIBhGn7VeWEFdRmYlqAuYtLKy39xIk4AAIhBgACYMbYR15pbTj7qbrYOwQ", "cost": 3.00, "callback_data": "vote_option18"},
    {"option_key": "option19", "title": "Eid Mubarak-Holy Month Of Ramadan", "file_id": "BAACAgEAAxkBAAIBhmn7VlZbc9yULfnQSho7VZy3uBziAAIiBgACYMbYR6_lK1s0AAG4mjsE", "cost": 3.00, "callback_data": "vote_option19"},
    {"option_key": "option20", "title": "The Freaky Friday Night (Part II)", "file_id": "BAACAgEAAxkBAAIBiGn7WE65QNeRm5585PfcTF689cnSAAIjBgACYMbYRw5_Mo57gZs-OwQ", "cost": 3.00, "callback_data": "vote_option20"},
]


def get_connection() -> sqlite3.Connection:
    DB_PATH.parent.mkdir(parents=True, exist_ok=True)
    connection = sqlite3.connect(DB_PATH)
    connection.row_factory = sqlite3.Row
    connection.execute("PRAGMA foreign_keys = ON")
    return connection


def init_db() -> None:
    with get_connection() as connection:
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS videos (
                option_key TEXT PRIMARY KEY,
                title TEXT NOT NULL,
                file_id TEXT NOT NULL DEFAULT '',
                cost REAL NOT NULL,
                callback_data TEXT NOT NULL UNIQUE
            )
            """
        )
        connection.execute(
            """
            CREATE TABLE IF NOT EXISTS votes (
                user_id INTEGER NOT NULL,
                option_key TEXT NOT NULL,
                voted_at TEXT NOT NULL,
                UNIQUE(user_id, option_key),
                FOREIGN KEY(option_key) REFERENCES videos(option_key)
            )
            """
        )
        connection.executemany(
            """
            INSERT INTO videos (option_key, title, file_id, cost, callback_data)
            VALUES (:option_key, :title, :file_id, :cost, :callback_data)
            ON CONFLICT(option_key) DO UPDATE SET
                title = excluded.title,
                file_id = excluded.file_id,
                cost = excluded.cost,
                callback_data = excluded.callback_data
            """
            ,
            VIDEO_DATA,
        )


def is_admin(user_id: int) -> bool:
    return user_id in ADMIN_USER_IDS


def voting_closed() -> bool:
    return datetime.now(NEW_YORK) >= POLL_CLOSE


def load_videos() -> list[sqlite3.Row]:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT option_key, title, file_id, cost, callback_data
            FROM videos
            ORDER BY CAST(SUBSTR(option_key, 7) AS INTEGER)
            """
        ).fetchall()


def record_vote(user_id: int, option_key: str) -> bool:
    with get_connection() as connection:
        cursor = connection.execute(
            """
            INSERT OR IGNORE INTO votes (user_id, option_key, voted_at)
            VALUES (?, ?, ?)
            """,
            (user_id, option_key, datetime.now(NEW_YORK).isoformat()),
        )
        return cursor.rowcount == 1


def get_results_rows() -> list[sqlite3.Row]:
    with get_connection() as connection:
        return connection.execute(
            """
            SELECT
                v.option_key,
                v.title,
                v.cost,
                COUNT(vt.user_id) AS vote_count
            FROM videos v
            LEFT JOIN votes vt ON vt.option_key = v.option_key
            GROUP BY v.option_key, v.title, v.cost
            ORDER BY vote_count DESC, v.option_key ASC
            """
        ).fetchall()


def callback_to_option_key(callback_data: str) -> str | None:
    for item in VIDEO_DATA:
        if item["callback_data"] == callback_data:
            return item["option_key"]
    return None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    close_label = POLL_CLOSE.strftime("%B %d, %Y at %I:%M %p %Z")
    intro = (
        "🇳🇬 <b>Wild Lagos PPV Poll</b> 🇳🇬\n\n"
        "🎬 The videos below are scene previews.\n"
        "🗳️ Vote for any scenes you want.\n"
        "✅ You can vote once per scene.\n\n"
        f"⏰ Voting closes on <b>{close_label}</b>."
    )
    await update.message.reply_text(intro, parse_mode=ParseMode.HTML)

    for video in load_videos():
        text = (
            f"🎬 <b>{video['title']}</b>\n"
            f"💵 Cost: ${video['cost']:.2f}\n\n"
            "<b>Tap below to vote for this scene.</b>"
        )
        markup = InlineKeyboardMarkup(
            [[InlineKeyboardButton("Vote for this scene", callback_data=video["callback_data"])]]
        )

        if video["file_id"]:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML)
            await update.message.reply_video(
                video=video["file_id"],
                reply_markup=markup,
            )
        else:
            await update.message.reply_text(text, parse_mode=ParseMode.HTML, reply_markup=markup)


async def vote(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = update.callback_query
    if query is None:
        return

    if voting_closed():
        await query.answer("Voting is closed for this poll.", show_alert=True)
        return

    option_key = callback_to_option_key(query.data)
    if option_key is None:
        await query.answer("Unknown option.", show_alert=True)
        return

    recorded = record_vote(query.from_user.id, option_key)
    if not recorded:
        await query.answer("You already voted for this scene.", show_alert=True)
        return

    await query.answer("Vote recorded.", show_alert=True)


async def results(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None:
        return

    user_id = update.effective_user.id if update.effective_user else None
    if user_id is None or not is_admin(user_id):
        await update.message.reply_text("This command is restricted.")
        return

    rows = get_results_rows()
    total_votes = sum(row["vote_count"] for row in rows)
    lines = [f"Results as of {datetime.now(NEW_YORK).strftime('%Y-%m-%d %I:%M:%S %p %Z')}"]
    lines.append(f"Total votes: {total_votes}")
    lines.append("")

    for index, row in enumerate(rows, start=1):
        lines.append(
            f"{index}. {row['title']} ({row['option_key']}) - {row['vote_count']} votes - ${row['cost']:.2f}"
        )

    await update.message.reply_text("\n".join(lines))


async def debug_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if update.message is None or update.message.video is None:
        return

    user_id = update.effective_user.id if update.effective_user else None
    if user_id is None or not is_admin(user_id):
        return

    await update.message.reply_text(update.message.video.file_id)


def main() -> None:
    init_db()
    asyncio.set_event_loop(asyncio.new_event_loop())
    application = Application.builder().token(BOT_TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("results", results))
    application.add_handler(CallbackQueryHandler(vote))
    application.add_handler(MessageHandler(filters.VIDEO, debug_video))
    LOGGER.info("Starting bot with database at %s", DB_PATH)
    application.run_polling()


if __name__ == "__main__":
    main()
