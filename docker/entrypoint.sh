#!/usr/bin/env sh
set -e

if [ "${RUN_MIGRATIONS:-1}" = "1" ]; then
  attempts="${MIGRATION_ATTEMPTS:-12}"
  count=1
  until python manage.py migrate --noinput; do
    if [ "$count" -ge "$attempts" ]; then
      echo "Migrations failed after $attempts attempts."
      exit 1
    fi
    count=$((count + 1))
    echo "Database is not ready yet. Retrying migrations ($count/$attempts)..."
    sleep 2
  done
fi

if [ "${COLLECTSTATIC:-0}" = "1" ]; then
  python manage.py collectstatic --noinput
fi

exec "$@"
