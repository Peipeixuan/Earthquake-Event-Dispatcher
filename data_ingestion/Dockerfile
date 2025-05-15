FROM python:3.10-slim

# Install tini
RUN apt-get update && apt-get install -y tini && rm -rf /var/lib/apt/lists/*

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade -r requirements.txt

COPY . .

ENTRYPOINT ["/usr/bin/tini", "--"]

CMD ["python", "main.py"]