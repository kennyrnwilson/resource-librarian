#!/bin/bash
# Quick check script - runs all CI/CD checks locally
# Usage: ./check.sh

set -e

echo "🔍 Running all CI/CD checks locally..."
echo ""

# Activate virtual environment
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Run: python -m venv venv"
    exit 1
fi

source venv/bin/activate

# Run Ruff linting
echo "📋 Running Ruff linting..."
ruff check .
echo "✅ Linting passed"
echo ""

# Run Ruff formatting check
echo "🎨 Checking code formatting..."
ruff format --check .
echo "✅ Formatting check passed"
echo ""

# Run tests with coverage
echo "🧪 Running tests with coverage..."
pytest --cov=src/resourcelibrarian --cov-report=term-missing
echo "✅ All tests passed"
echo ""

echo "✅ All checks passed! Safe to push."
