#!/bin/bash
set -e

echo "ResistanceAtlas — starting up"
echo "==============================="

# Check .env exists
if [ ! -f ".env" ]; then
  echo "ERROR: .env file not found."
  echo "Copy .env.example to .env and add your NVIDIA API key:"
  echo "  cp .env.example .env"
  echo "  # Then edit .env and add NVIDIA_API_KEY=your_key_here"
  exit 1
fi

# Check NVIDIA_API_KEY is set
if ! grep -q "NVIDIA_API_KEY=nvapi" .env; then
  echo "WARNING: NVIDIA_API_KEY may not be set correctly in .env"
  echo "Get a free key at: https://build.nvidia.com/arc/evo2-40b"
fi

echo "Starting services with Docker Compose..."
docker compose up --build

echo ""
echo "ResistanceAtlas is running:"
echo "  Frontend: http://localhost:3000"
echo "  Backend:  http://localhost:8000"
echo "  API docs: http://localhost:8000/docs"
