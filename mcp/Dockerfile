FROM python:3.13-slim

WORKDIR /app
COPY requirements.txt .
RUN pip --no-cache-dir install -r requirements.txt
COPY server.py .

ENV MARKITDOWN_API_URL=http://api:8000

CMD ["python", "server.py"]
