
# config.py

# =====================================
# TELEGRAM BOT CONFIGURATION
# =====================================

TELEGRAM_BOT_TOKEN = ""


# =====================================
# VIDEO CONFIGURATION
# =====================================

MAX_VIDEO_MB = 20
MAX_VIDEO_SECONDS = 300
MAX_OUTPUT_MB = 49


# =====================================
# PROCESSING CONFIGURATION
# =====================================

PROCESSING_TIMEOUT_SECONDS = 2700
MAX_CONCURRENT_PROCESSING = 1


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
