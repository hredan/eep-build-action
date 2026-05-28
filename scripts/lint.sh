#!/bin/bash

# Script to run pylint and pyright locally with the same configuration as the GitHub workflow

set -e

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

echo -e "${BLUE}=== Python Code Quality Checks ===${NC}\n"

# Check if virtual environment is active, if not try to activate it
if [ -z "$VIRTUAL_ENV" ]; then
    if [ -d ".venv" ]; then
        echo -e "${YELLOW}Activating virtual environment...${NC}"
        source .venv/bin/activate
    else
        echo -e "${YELLOW}No virtual environment found. Using system Python.${NC}"
    fi
fi

# Install dependencies
echo -e "${YELLOW}Installing dependencies...${NC}"
python -m pip install --upgrade pip > /dev/null 2>&1
python -m pip install pylint pyright > /dev/null 2>&1
if [ -f "requirements.txt" ]; then
    python -m pip install -r requirements.txt > /dev/null 2>&1
fi
echo -e "${GREEN}Dependencies installed${NC}\n"

# Run pylint
echo -e "${BLUE}--- Running pylint ---${NC}"
if python -m pylint --max-line-length=120 py_modules/ build_sketch.py 2>/dev/null; then
    echo -e "${GREEN}✓ pylint passed${NC}\n"
    PYLINT_RESULT=0
else
    PYLINT_RESULT=$?
    echo -e "${RED}✗ pylint found issues${NC}\n"
fi

# Run pyright
echo -e "${BLUE}--- Running pyright ---${NC}"
if python -m pyright > /dev/null 2>&1; then
    echo -e "${GREEN}✓ pyright passed${NC}\n"
    PYRIGHT_RESULT=0
else
    PYRIGHT_RESULT=$?
    echo -e "${RED}✗ pyright found issues${NC}\n"
fi

# Summary
echo -e "${BLUE}=== Summary ===${NC}"
if [ $PYLINT_RESULT -eq 0 ] && [ $PYRIGHT_RESULT -eq 0 ]; then
    echo -e "${GREEN}All checks passed!${NC}"
    exit 0
else
    echo -e "${RED}Some checks failed.${NC}"
    exit 1
fi
