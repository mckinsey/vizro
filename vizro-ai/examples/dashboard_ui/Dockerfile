FROM python:3.12-slim

# Install lsof
RUN apt-get update && apt-get install -y lsof && rm -rf /var/lib/apt/lists/*

RUN useradd -m -u 1000 user

WORKDIR /app

COPY --chown=user ./requirements.txt requirements.txt

RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY --chown=user . /app

EXPOSE 7868 8051

USER user

CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:7868", "--timeout", "180", "app:server"]