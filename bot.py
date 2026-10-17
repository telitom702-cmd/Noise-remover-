from __future__ import annotations

import asyncio
import logging
import os
import tempfile
import time
from pathlib import Path

from telegram import Update
from telegram.error import TelegramError
from telegram.ext import (
    Application,
    ApplicationBuilder,
    CommandHandler,
    ContextTypes,
    MessageHandler,
    filters,
)

from audio_processor import InputValidationError, MediaProcessingError, process_video

LOGGER = logging.getLogger("noise_remover_bot")
MAX_VIDEO_MB = int(os.getenv("MAX_VIDEO_MB", "20"))
MAX_VIDEO_SECONDS = int(os.getenv("MAX_VIDEO_SECONDS", "300"))
MAX_OUTPUT_MB = int(os.getenv("MAX_OUTPUT_MB", "49"))
PROCESSING_TIMEOUT_SECONDS = int(
    os.getenv("PROCESSING_TIMEOUT_SECONDS", str(45 * 60))
)

# Demucs can use substantial memory and CPU. Serial processing keeps one busy
# video from making the bot unreliable for every other user.
PROCESSING_SLOT = asyncio.Semaphore(1)

WELCOME_TEXT = (
    "ভিডিও পাঠান—আমি ব্যাকগ্রাউন্ড মিউজিক কমিয়ে কথা/কণ্ঠ যতটা সম্ভব রেখে "
    "প্রসেস করা ভিডিও ফেরত দেব।\n\n"
    f"সর্বোচ্চ ভিডিও: {MAX_VIDEO_MB} MB, {MAX_VIDEO_SECONDS // 60} মিনিট। "
    "শুধু মিউজিক থাকলে সেটিও সরিয়ে যাবে।"
)


def _uploaded_video(message):
    if message.video:
        return message.video, ".mp4"

    document = message.document
    if document and document.mime_type and document.mime_type.startswith("video/"):
        extension = Path(document.file_name or "").suffix.lower()
        if extension not in {".mp4", ".mov", ".mkv", ".webm", ".avi", ".m4v"}:
            extension = ".video"
        return document, extension

    return None, None


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text(WELCOME_TEXT)


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    del context
    if update.message:
        await update.message.reply_text(
            "ভিডিও বা ভিডিও-ফাইল পাঠালেই প্রসেস শুরু হবে। "
            "কথা রেখে ব্যাকগ্রাউন্ড মিউজিক সরাতে AI source separation ব্যবহার করি।\n\n"
            f"সীমা: {MAX_VIDEO_MB} MB এবং {MAX_VIDEO_SECONDS} সেকেন্ড।\n"
            "প্রথম ভিডিওতে AI মডেল ডাউনলোড হতে সময় লাগতে পারে।"
        )


async def _processing_updates(status_message, done: asyncio.Event) -> None:
    started = time.monotonic()
    while not done.is_set():
        try:
            await asyncio.wait_for(done.wait(), timeout=30)
            return
        except TimeoutError:
            elapsed = int(time.monotonic() - started)
            minutes, seconds = divmod(elapsed, 60)
            try:
                await status_message.edit_text(
                    "মিউজিক আলাদা করা হচ্ছে "
                    f"({minutes} মিনিট {seconds} সেকেন্ড)। কাজ শেষ হলে ভিডিও পাঠাব।"
                )
            except TelegramError:
                # The user may have deleted the status message; processing
                # should continue and the result can still be delivered.
                return


async def handle_video(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    message = update.message
    if not message:
        return

    uploaded, extension = _uploaded_video(message)
    if uploaded is None:
        await message.reply_text("একটি ভিডিও পাঠান, অথবা /help লিখুন।")
        return

    file_size = uploaded.file_size or 0
    max_input_bytes = MAX_VIDEO_MB * 1024 * 1024
    if file_size > max_input_bytes:
        await message.reply_text(
            f"ভিডিওটি {MAX_VIDEO_MB} MB সীমার চেয়ে বড়। ছোট বা কম রেজল্যুশনের ভিডিও পাঠান।"
        )
        return

    duration = getattr(uploaded, "duration", None)
    if duration and duration > MAX_VIDEO_SECONDS:
        await message.reply_text(
            f"ভিডিওটি {MAX_VIDEO_SECONDS // 60} মিনিটের বেশি। ছোট ভিডিও পাঠান।"
        )
        return

    if PROCESSING_SLOT.locked():
        status_message = await message.reply_text(
            "অন্য একটি ভিডিও প্রসেস হচ্ছে; আপনার ভিডিওটি সারিতে রাখা হয়েছে।"
        )
    else:
        status_message = await message.reply_text("ভিডিও গ্রহণ করা হয়েছে।")

    await PROCESSING_SLOT.acquire()
    try:
        await status_message.edit_text("ভিডিও ডাউনলোড করা হচ্ছে…")
        with tempfile.TemporaryDirectory(prefix="noise-remover-") as temp_dir:
            work_dir = Path(temp_dir)
            input_path = work_dir / f"input{extension}"
            output_path = work_dir / "video-without-background-music.mp4"

            telegram_file = await context.bot.get_file(uploaded.file_id)
            await telegram_file.download_to_drive(custom_path=str(input_path))

            await status_message.edit_text(
                "AI দিয়ে ব্যাকগ্রাউন্ড মিউজিক আলাদা করা হচ্ছে। "
                "প্রথমবার মডেল ডাউনলোডে একটু বেশি সময় লাগতে পারে…"
            )
            finished = asyncio.Event()
            progress_task = asyncio.create_task(
                _processing_updates(status_message, finished)
            )
            try:
                await asyncio.to_thread(
                    process_video,
                    input_path,
                    output_path,
                    max_input_bytes=max_input_bytes,
                    max_duration_seconds=MAX_VIDEO_SECONDS,
                    max_output_bytes=MAX_OUTPUT_MB * 1024 * 1024,
                    timeout_seconds=PROCESSING_TIMEOUT_SECONDS,
                )
            finally:
                finished.set()
                await progress_task

            await status_message.edit_text("প্রসেস সম্পন্ন। ভিডিও পাঠানো হচ্ছে…")
            with output_path.open("rb") as processed_video:
                await context.bot.send_video(
                    chat_id=message.chat_id,
                    video=processed_video,
                    supports_streaming=True,
                    caption="ব্যাকগ্রাউন্ড মিউজিক কমানো ভিডিও",
                    read_timeout=120,
                    write_timeout=120,
                )
            await status_message.edit_text("ভিডিও পাঠানো হয়েছে।")
    except InputValidationError as exc:
        await status_message.edit_text(str(exc))
    except (MediaProcessingError, TelegramError, OSError, TimeoutError):
        LOGGER.exception("Video processing or delivery failed")
        try:
            await status_message.edit_text(
                "এই ভিডিওটি প্রসেস করা যায়নি। MP4 ভিডিও দিয়ে আবার চেষ্টা করুন।"
            )
        except TelegramError:
            pass
    except Exception:
        LOGGER.exception("Unexpected video processing error")
        try:
            await status_message.edit_text(
                "অপ্রত্যাশিত সমস্যা হয়েছে। কিছুক্ষণ পরে আবার চেষ্টা করুন।"
            )
        except TelegramError:
            pass
    finally:
        PROCESSING_SLOT.release()


async def handle_other_message(
    update: Update, context: ContextTypes.DEFAULT_TYPE
) -> None:
    del context
    if update.message:
        await update.message.reply_text("ভিডিও পাঠান, অথবা নির্দেশনার জন্য /help লিখুন।")


def main() -> None:
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN is missing. Add the token as a Replit Secret "
            "or an environment variable before starting the bot."
        )

    logging.basicConfig(
        level=os.getenv("LOG_LEVEL", "INFO").upper(),
        format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    )

    application: Application = (
        ApplicationBuilder().token(token).concurrent_updates(4).build()
    )
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(
        MessageHandler(filters.VIDEO | filters.Document.VIDEO, handle_video)
    )
    application.add_handler(
        MessageHandler(filters.ALL & ~filters.COMMAND, handle_other_message)
    )

    LOGGER.info("Telegram noise-removal bot is starting")
    application.run_polling(allowed_updates=Update.ALL_TYPES)


if __name__ == "__main__":
    main()
