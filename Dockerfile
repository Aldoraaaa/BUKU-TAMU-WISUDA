FROM python:3.11-slim

ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    DATA_DIR=/data

# Standar Keamanan: Buat user non-root UID 10001
RUN addgroup --system --gid 10001 appgroup && \
    adduser --system --uid 10001 --ingroup appgroup appuser

WORKDIR /app

# Alokasikan folder volume dengan kepemilikan appuser
RUN mkdir -p /data && chown -R appuser:appgroup /data /app

COPY --chown=appuser:appgroup app.py .
USER appuser

EXPOSE 5000

# Healthcheck bawaan kontainer untuk observabilitas
HEALTHCHECK --interval=15s --timeout=3s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:5000/health')" || exit 1

CMD ["python", "app.py"]