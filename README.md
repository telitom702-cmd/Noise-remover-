# Noise Remover Bot

Telegram bot that uses Demucs to separate vocals from background music in a
video, applies light noise cleanup, and sends back a video with the cleaned
audio. Processing runs on the CPU by default; the first run downloads the
Demucs model and can take a while.

## Recommended: run with Docker

Docker is the same setup on Windows, macOS, and Linux and includes FFmpeg.

1. Install Docker Desktop (Windows/macOS) or Docker Engine and the Compose
   plugin (Linux).
2. Copy `.env.example` to `.env` (`Copy-Item .env.example .env` in PowerShell).
3. Create a Telegram bot with BotFather and put its token in `.env` as
   `TELEGRAM_BOT_TOKEN=...`. Keep `.env` private; never commit or share it.
4. In this directory, run:

   ```sh
   docker compose up --build -d
   docker compose logs -f
   ```

   Stop it with `docker compose down`. The named Docker volume preserves the
   downloaded model between container runs.

## Run directly on your computer

Use Python 3.10 or newer and install FFmpeg so both `ffmpeg` and `ffprobe` are
available on `PATH`. On Windows, add FFmpeg's `bin` directory to `PATH`.

```sh
python -m venv .venv
```

Activate the environment:

```sh
# macOS / Linux
source .venv/bin/activate

# Windows PowerShell
.venv\Scripts\Activate.ps1
```

Then install dependencies, prepare the local environment file, and start the
bot:

```sh
python -m pip install -r requirements.txt
```

Copy `.env.example` to `.env`, set `TELEGRAM_BOT_TOKEN` in it, then run:

```sh
python bot.py
```

The `.env` file is loaded automatically. Never commit it or paste the token
into chat.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | (required) | Token from BotFather |
| `MAX_VIDEO_MB` | `20` | Maximum uploaded video size |
| `MAX_VIDEO_SECONDS` | `300` | Maximum video duration |
| `MAX_OUTPUT_MB` | `49` | Maximum output size sent by the bot |
| `PROCESSING_TIMEOUT_SECONDS` | `2700` | Total processing time limit per video |
| `MAX_CONCURRENT_PROCESSING` | `1` | Number of videos processed at once |
| `DEMUCS_MODEL` | `htdemucs` | Demucs model name |
| `DEMUCS_DEVICE` | `cpu` | Processing device; CPU works without a GPU |
| `DEMUCS_SHIFTS` | `1` | Demucs quality/speed setting (1–10) |

The bot needs internet access to reach Telegram and download the model on the
first run. CPU processing can be slow, especially for long videos. Docker is
the most repeatable option when you want the same FFmpeg and Python setup on
different operating systems.

## Tests

Run the standard-library unit tests with:

```sh
python -m unittest discover -s tests -v
```
