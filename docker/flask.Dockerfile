# syntax=docker/dockerfile:1
#
# Production image for the Flask backend (backend/flask/final_project).
# Build from the repository root:
#
#   docker build -f docker/flask.Dockerfile -t soft-eng-flask .

FROM python:3.12-slim AS base
WORKDIR /app

FROM base AS deps
COPY backend/flask/final_project/requirements.txt ./
RUN pip install --no-cache-dir --timeout=120 -r requirements.txt

FROM base AS runner
COPY --from=deps /usr/local/lib/python3.12 /usr/local/lib/python3.12
COPY --from=deps /usr/local/bin /usr/local/bin
COPY backend/flask/final_project/ ./

ENV FLASK_APP=main:app
ENV FLASK_DEBUG=0
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1

EXPOSE 5000

CMD ["python", "main.py"]