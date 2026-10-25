FROM python:3.13-slim
WORKDIR /app/engine
RUN pip install --no-cache-dir sxtwl ephem tzdata fastapi uvicorn skyfield numpy
COPY engine/ /app/engine/
ENV PORT=8000 PYTHONPATH=/app/engine
CMD ["sh", "-c", "uvicorn tvbt.api:app --host 0.0.0.0 --port ${PORT}"]
