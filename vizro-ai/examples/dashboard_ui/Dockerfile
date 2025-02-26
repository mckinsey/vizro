FROM python:3.12-slim AS builder

RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

COPY --chown=user requirements.txt .
RUN pip install --user --no-cache-dir --upgrade pip && \
    pip install --user --no-cache-dir -r requirements.txt

# Production stage
FROM python:3.12-slim

RUN apt-get update && apt-get upgrade -y && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user
USER user
ENV HOME=/home/user \
    PATH=/home/user/.local/bin:$PATH
WORKDIR $HOME/app

COPY --from=builder --chown=user $HOME/.local/lib/python3.12/site-packages $HOME/.local/lib/python3.12/site-packages
COPY --from=builder --chown=user $HOME/.local/bin $HOME/.local/bin

COPY --chown=user . $HOME/app

EXPOSE 7860

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7860", "app:app"]
