#!/bin/bash
# Simple helper to launch Codex CLI using Gemini provider with optional key rotation

if [ -z "$GEMINI_API_KEYS" ] && [ -n "$1" ]; then
  export GEMINI_API_KEYS="$1"
  shift
fi

# Default to gemini provider
export LLM_PROVIDER=gemini

# Forward all args to codex CLI
npx codex "$@"
