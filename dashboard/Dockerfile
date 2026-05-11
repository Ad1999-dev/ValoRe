FROM mirror.gcr.io/library/python:3.11-slim

WORKDIR /app

COPY --from=ghcr.io/astral-sh/uv:latest /uv /usr/local/bin/uv

COPY pyproject.toml uv.lock ./

RUN uv export --frozen --no-dev --no-hashes -o /tmp/requirements.txt && \
    uv pip install --system -r /tmp/requirements.txt

COPY Home.py ./
COPY pages/ ./pages/
COPY utils/ ./utils/

ENV PORT=8501

CMD streamlit run Home.py \
    --server.port=$PORT \
    --server.address=0.0.0.0 \
    --server.headless=true
