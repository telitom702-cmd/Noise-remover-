# Noise Remover Bot

Telegram bot that uses Demucs to separate vocals from background music in a
video, applies light noise cleanup, and sends back a video with the cleaned
audio. Processing runs on the CPU by default; the first run downloads the
Demucs model and can take a while.

## Recommended: run with Docker

Docker is the same setup on Windows, macOS, and Linux and includes FFmpeg.
The bot also exposes an HTTP health endpoint for web-service hosting.

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
   downloaded model between container runs. Open `http://localhost:8080/health`
   to confirm the web service is responding.

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

## Deploy as a web service

This keeps the existing Telegram interface and adds an HTTP endpoint for
hosting platforms that expect a web process:

- Start command: `python bot.py`
- Secret environment variable: `TELEGRAM_BOT_TOKEN`
- Listening address: `0.0.0.0:$PORT` (`PORT` defaults to `8080`)
- Health-check path: `/health` (returns HTTP 200 and JSON while the process is
  running)
- Run exactly one instance for a bot token; Telegram long polling cannot be
  shared by multiple replicas.

Use the included Dockerfile on platforms that support Docker, or install the
Python requirements and FFmpeg on a Python host. The HTTP endpoint is for
platform health checks; video uploads and results still go through Telegram.

## VPS deployment with Docker Compose

After the pull request is merged, use an Ubuntu or Debian VPS with Docker
Engine and the Compose plugin installed. A starting size of 4 vCPU and 8 GB
RAM is recommended for CPU-based Demucs; shorter videos may work on smaller
machines but will process more slowly.

```sh
git clone https://github.com/telitom702-cmd/Noise-remover-.git
cd Noise-remover-
cp .env.example .env
nano .env
```

Set `TELEGRAM_BOT_TOKEN` in `.env`, save it, then start the service:

```sh
docker compose up --build -d
docker compose ps
curl -fsS http://127.0.0.1:8080/health
docker compose logs -f --tail=100
```

Compose binds the health endpoint to `127.0.0.1`, so port `8080` is not
published on the VPS's public network interface. No inbound app port is needed
for Telegram polling; keep SSH access restricted as usual. The model cache is
stored in a Docker volume and survives container rebuilds. Run one instance
per bot token.

To update after a new version is merged:

```sh
git pull --ff-only
docker compose up --build -d
```

Stop the bot with `docker compose down`. Do not delete the `demucs-cache`
volume unless you also want to remove the downloaded model.

## Configuration

| Variable | Default | Purpose |
| --- | --- | --- |
| `TELEGRAM_BOT_TOKEN` | (required) | Token from BotFather |
| `PORT` | `8080` | HTTP port used by the web-service health endpoint |
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
