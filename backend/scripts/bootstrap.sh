#!/usr/bin/env bash
set -euo pipefail

echo "[bootstrap] Ensuring .env..."
cp -n .env.example .env || true

echo "[bootstrap] Building containers..."
docker-compose build

echo "[bootstrap] Starting services..."
docker-compose up -d

echo "[bootstrap] Dev server ready at http://localhost:8000"
