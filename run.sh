#!/usr/bin/env bash
# ==============================================================================
# 1-Click Startup & Demonstration Script for Scholarship Intelligence Crawler
# ==============================================================================

set -e

echo "================================================================================"
echo "⚡ Scholarship Intelligence Crawler (Edxso AI Engineer Intern Assignment 2)"
echo "================================================================================"

# 1. Initialize and Seed Database
echo "📦 [1/3] Seeding 24 Authentic Indian Scholarships..."
python3 scripts/seed_data.py

# 2. Run Test Suite
echo ""
echo "🧪 [2/3] Running Validation Test Suite..."
python3 -m pytest tests/

# 3. Start Web Dashboard
echo ""
echo "🚀 [3/3] Starting FastAPI Server & Web Dashboard on http://localhost:8000 ..."
echo "👉 Open http://localhost:8000 in your browser to view the interactive dashboard."
echo "👉 API Documentation available at http://localhost:8000/docs"
echo "Press Ctrl+C to terminate."
echo ""

uvicorn app.api.main:app --host 0.0.0.0 --port 8000 --reload
