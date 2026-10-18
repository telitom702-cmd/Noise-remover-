
import os

try:
    from dotenv import load_dotenv
except ImportError:
    # Running the unit tests without installing dependencies is still useful.
    load_dotenv = None

if load_dotenv is not None:
    load_dotenv()


def _positive_int_env(name: str, default: int) -> int:
    raw_value = os.getenv(name)
    if raw_value is None or not raw_value.strip():
        return default

    try:
        value = int(raw_value)
    except ValueError as exc:
        raise RuntimeError(f"{name} must be a positive integer.") from exc

    if value < 1:
        raise RuntimeError(f"{name} must be a positive integer.")
    return value


# Keep credentials out of source control; load them from the environment or .env.
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN", "").strip()


# =====================================
# VIDEO CONFIGURATION
# =====================================

MAX_VIDEO_MB = _positive_int_env("MAX_VIDEO_MB", 20)
MAX_VIDEO_SECONDS = _positive_int_env("MAX_VIDEO_SECONDS", 300)
MAX_OUTPUT_MB = _positive_int_env("MAX_OUTPUT_MB", 49)


# =====================================
# PROCESSING CONFIGURATION
# =====================================

PROCESSING_TIMEOUT_SECONDS = _positive_int_env(
    "PROCESSING_TIMEOUT_SECONDS", 2700
)
MAX_CONCURRENT_PROCESSING = _positive_int_env(
    "MAX_CONCURRENT_PROCESSING", 1
)


# =====================================
# BOT MESSAGES
# =====================================

WELCOME_TEXT = (
    "ভিডিও পাঠান—আমি ব্যাকগ্রাউন্ড মিউজিক কমিয়ে "
    "কথা/কণ্ঠ যতটা সম্ভব রেখে ভিডিও ফেরত দেব।\n\n"
    f"সর্বোচ্চ ভিডিও সাইজ: {MAX_VIDEO_MB} MB\n"
    f"সর্বোচ্চ দৈর্ঘ্য: {MAX_VIDEO_SECONDS} সেকেন্ড।"
)

HELP_TEXT = (
    "ভিডিও বা ভিডিও ফাইল পাঠান।\n"
    "AI দিয়ে ব্যাকগ্রাউন্ড মিউজিক কমানোর চেষ্টা করা হবে।\n\n"
    f"সর্বোচ্চ সাইজ: {MAX_VIDEO_MB} MB\n"
    f"সর্বোচ্চ দৈর্ঘ্য: {MAX_VIDEO_SECONDS} সেকেন্ড।"
)
