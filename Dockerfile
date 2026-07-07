# Simple Dockerfile for GenAI App
# Build: docker build -f Dockerfile.genai -t genai-app .
# Run: docker run -p 8000:8000 --env-file .env genai-app

FROM python:3.11-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY genai_app.py .

EXPOSE 8000

CMD ["uvicorn", "genai_app:app", "--host", "0.0.0.0", "--port", "8000"]
