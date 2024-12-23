#!/bin/bash

# Exit on error
set -e

echo "🔍 Running type checking with mypy..."
poetry run mypy pepperpy_core tests

echo "🧹 Running linting with ruff..."
poetry run ruff check .

echo "✨ Running code formatting with ruff format..."
poetry run ruff format .

echo "🧪 Running tests with pytest..."
poetry run pytest --cov=pepperpy_core --cov-report=term-missing

echo "✅ All checks passed!" 