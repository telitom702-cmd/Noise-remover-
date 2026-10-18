
FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PIP_NO_CACHE_DIR=1
ENV TORCH_HOME=/home/app/.cache/torch

WORKDIR /app

# FFmpeg is required for probing, extracting audio, and exporting video.
RUN apt-get update && apt-get install -y --no-install-recommends \
    ffmpeg \
    libsndfile1 \
    ca-certificates \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies before copying the application for better caching.
COPY requirements.txt ./
RUN python -m pip install --upgrade pip \
    && python -m pip install -r requirements.txt

# Run as an unprivileged user. The writable cache keeps Demucs models between runs.
RUN groupadd --system app \
    && useradd --system --gid app --create-home --home-dir /home/app app \
    && mkdir -p /home/app/.cache/torch \
    && chown -R app:app /home/app

COPY --chown=app:app . .
USER app

CMD ["python", "bot.py"]
