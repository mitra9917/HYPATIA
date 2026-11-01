FROM python:3.12-slim

WORKDIR /app
RUN apt-get update && apt-get install -y --no-install-recommends libgl1 libglib2.0-0 \
  && rm -rf /var/lib/apt/lists/*

COPY services/api/requirements.txt /app/requirements.txt
RUN pip install --no-cache-dir -r /app/requirements.txt

COPY services/api/hypatia /app/hypatia
ENV PYTHONPATH=/app
ENV PORT=8000
EXPOSE 8000
CMD ["uvicorn", "hypatia.app:app", "--host", "0.0.0.0", "--port", "8000"]
