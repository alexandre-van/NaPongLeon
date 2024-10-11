#!/bin/bash

if [ -z "$1" ]; then
  echo "Use: $0 <filename>"
  exit 1
fi

FILENAME=$1

if [ ! -f "$FILENAME" ]; then
  echo "File '$FILENAME' does not exist"
  exit 1
fi

TEMPFILE=$(mktemp)

replace_env_vars() {
  local line="$1"
  while [[ "$line" =~ (\$[A-Z_][A-Z0-9_]*) ]]; do
    full_match="${BASH_REMATCH[1]}"
    var="${full_match:1}"
    if [ -n "${!var}" ]; then
      value="${!var}"
      line="${line//$full_match/$value}"
    else
      line="${line//$full_match/}"
    fi
  done
  echo "$line"
}

while IFS= read -r line; do
  replace_env_vars "$line" >> "$TEMPFILE"
done < "$FILENAME"

mv "$TEMPFILE" "$FILENAME"

echo "Environment variables have been replaced in file '$FILENAME'"