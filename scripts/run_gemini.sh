#!/bin/bash
# Simple helper to launch Codex CLI using Gemini provider with optional key rotation

if [ -z "$GEMINI_API_KEYS" ]; then
  if [ -n "$1" ]; then
    export GEMINI_API_KEYS="$1"
    shift
  else
    # Default to built-in keys if none provided
    export GEMINI_API_KEYS="AIzaSyC4Wvi3dGfxILk37TRnhON_vcWgZi09ahQ,\
AIzaSyDb9GBb0v5VU9Qx9eQbbkdOZYjtnRvaJ60,\
AIzaSyAwS8GQTjCJWjfbGD8G6_WwHIe4cRpEfxI,\
AIzaSyCjcUwsISnTk8MBUeU0jX2EwKzE-KQOYDY,\
AIzaSyBh1D_sPGa9d9mX8XfiTF3E4iZKjB8hQ7k,\
AIzaSyB-4dpI0kAcE3T3Jb4e_NKuvvXy9_HXHcE"
  fi
fi

# Default to gemini provider
export LLM_PROVIDER=gemini

# Forward all args to codex CLI
npx codex "$@"
